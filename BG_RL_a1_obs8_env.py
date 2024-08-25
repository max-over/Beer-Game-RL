import random
import gymnasium
random.seed(10)

from gymnasium import spaces
import numpy as np


class BeerGameEnv(gymnasium.Env):

    def __init__(self):
        super(BeerGameEnv, self).__init__()

        import ret_no_gui
        import distr_no_gui
        import whole_no_gui
        import plant_no_gui

        self.ret = ret_no_gui.Retailer()
        self.distr = distr_no_gui.Distributor()
        self.whole = whole_no_gui.Wholesaler()
        self.plant = plant_no_gui.Plant()

        self.ret.holdingrate = 4
        self.ret.backlograte = 10 #10 #1000
        self.ret.leadtimeup = 2
        self.distr.holdingrate = 2
        self.distr.backlograte = 4
        self.distr.leadtimeup = 2
        self.whole.holdingrate = 2
        self.whole.backlograte = 4
        self.whole.leadtimeup = 2
        self.plant.holdingrate_raw = 1
        self.plant.holdingrate_finished = 2
        self.plant.backlograte = 4
        self.plant.leadtimeup = 2
        self.plant.productiontime = 2
        self.periods = 1000
        self.current_period = 0

        high = np.array(
            [
                200,
                200,
                200,
                200,
                200,
                1000,
                1000,
                1000
            ],
            dtype=np.int32,
        )

        self.action_space = spaces.MultiDiscrete([30], dtype=np.int32)
        self.observation_space = spaces.Box(0, high, dtype=np.int32)
        self.state = None

    def step(self, action):

        self.current_period += 1
        self.ret.current_demand = int(random.uniform(8,13))
        self.ret.current_period = self.current_period
        self.distr.current_period = self.current_period
        self.whole.current_period = self.current_period
        self.plant.current_period = self.current_period

        self.ret.update()
        self.ret_order = action[0]

        self.distr.ret_order = self.ret_order
        self.distr.update()
        self.ret.shipment_ret_queue.append((self.distr.shipment, self.current_period))
        self.distr_order = max(self.distr.targetstock - self.distr.inventory, 0)

        self.whole.distr_order = self.distr_order
        self.whole.update()
        self.distr.shipment_distr_queue.append((self.whole.shipment, self.current_period))
        self.whole_order = max(self.whole.targetstock - self.whole.inventory, 0)

        self.plant.whole_order = self.whole_order
        self.plant.update()
        self.plant.update_costs()
        self.plant.production = max(self.plant.targetstock_finished - self.plant.inventory_finished, 0)
        self.plant.produce()
        self.plant.prod_order = max(self.plant.targetstock_raw - self.plant.inventory_raw, 0)
        self.plant.plant_order()
        self.whole.shipment_whole_queue.append((self.plant.shipment, self.current_period))

        reward = -(self.ret.periodcosts + self.distr.periodcosts + self.whole.periodcosts + self.plant.periodcosts) / 10000

        if self.current_period >= self.periods:
            done = True
            reward2 = -(self.ret.costs + self.distr.costs + self.whole.costs + self.plant.costs)/10000
            print(f"total costs: {reward2*10000}")
            print(f"ret_sl: {self.ret.sl}")
            print(f"distr_sl: {self.distr.sl}")
            print(f"whole_sl: {self.whole.sl}")
            print(f"plant_sl: {self.plant.sl}")

        else:
            done = False

        info = {}

        self.state = [self.ret.inventory, self.distr.inventory, self.whole.inventory, self.plant.inventory_raw,
                      self.plant.inventory_finished, self.distr.backlogtotal, self.whole.backlogtotal, self.plant.backlogtotal]
        self.state = np.array(self.state, dtype=np.int32)

        return self.state, reward, done, False, info


    def reset(self, seed=None, options=None):
        self.ret_order = 0
        self.distr_order = 0
        self.whole_order = 0
        self.plant_prod_order = 0
        self.plant.production = 0

        self.ret.inventory = 20
        self.distr.inventory = 20
        self.whole.inventory = 20
        self.plant.inventory_raw = 20
        self.plant.inventory_finished = 20
        self.current_period = 0

        self.ret.inventorycosts = 0
        self.ret.backlogcosts = 0
        self.ret.backlogtotal = 0
        self.ret.backlogcount = 0

        self.distr.inventorycosts = 0
        self.distr.backlogcosts = 0
        self.distr.backlogtotal = 0
        self.distr.backlogcount = 0


        self.whole.inventorycosts = 0
        self.whole.backlogcosts = 0
        self.whole.backlogtotal = 0
        self.whole.backlogcount = 0

        self.plant.inventorycosts = 0
        self.plant.backlogcosts = 0
        self.plant.backlogtotal = 0
        self.plant.backlogcount = 0

        self.ret.targetstock = 22
        self.distr.targetstock = 22
        self.whole.targetstock = 19
        self.plant.targetstock_raw = 18
        self.plant.targetstock_finished = 29

        self.ret.sl = 1
        self.distr.sl = 1
        self.whole.sl = 1
        self.plant.sl = 1

        self.state = [self.ret.inventory, self.distr.inventory, self.whole.inventory, self.plant.inventory_raw,
                      self.plant.inventory_finished, self.distr.backlogtotal, self.whole.backlogtotal, self.plant.backlogtotal]

        self.state = np.array(self.state,dtype=np.int32)

        info = {}

        return self.state, info





