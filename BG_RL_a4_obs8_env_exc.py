import random
import gymnasium
random.seed(10)

import time
from xlwt import Workbook

xtime = str(round(time.time()))

wb = Workbook()

sheet_ret = wb.add_sheet("E4")
sheet_ret.write(0, 0, "demand")
sheet_ret.write(0, 1, "inv_ret_start")
sheet_ret.write(0, 2, "inv_distr_start")
sheet_ret.write(0, 3, "inv_whole_start")
sheet_ret.write(0, 4, "inv_plant_fg_start")
sheet_ret.write(0, 5, "inv_plant_raw_start")

sheet_ret.write(0, 6, "ret_order")
sheet_ret.write(0, 7, "distr_order")
sheet_ret.write(0, 8, "whole_order")
sheet_ret.write(0, 9, "plant_fg_order")
sheet_ret.write(0, 10, "plant_raw_prod")

sheet_ret.write(0, 11, "inv_ret_end")
sheet_ret.write(0, 12, "inv_distr_end")
sheet_ret.write(0, 13, "inv_whole_end")
sheet_ret.write(0, 14, "inv_plant_fg_end")
sheet_ret.write(0, 15, "inv_okant_raw_end")

sheet_ret.write(0, 16, "ret_shp")
sheet_ret.write(0, 17, "distr_shp")
sheet_ret.write(0, 18, "whole_shp")
sheet_ret.write(0, 19, "plant_fg_shp")
sheet_ret.write(0, 20, "plant_raw_shp")

sheet_ret.write(0, 21, "ret_costs")
sheet_ret.write(0, 22, "distr_costs")
sheet_ret.write(0, 23, "whole_costs")
sheet_ret.write(0, 24, "plant_fg_costs")


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
        self.ret.backlograte = 10 #10 #10000
        self.ret.leadtimeup = 2
        self.distr.holdingrate = 2
        self.distr.backlograte = 4 #4 #1000
        self.distr.leadtimeup = 2
        self.whole.holdingrate = 2
        self.whole.backlograte = 4 #4 #100
        self.whole.leadtimeup = 2
        self.plant.holdingrate_raw = 1
        self.plant.holdingrate_finished = 2
        self.plant.backlograte = 4 #4 #10
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

        self.action_space = spaces.MultiDiscrete([30,30,30,30], dtype=np.int32)
        self.observation_space = spaces.Box(0, high, dtype=np.int32)
        self.state = None

    def step(self, action):

        self.current_period += 1
        self.ret.current_demand = int(random.uniform(8,12))
        #self.ret.current_demand = 10
        self.ret.current_period = self.current_period
        self.distr.current_period = self.current_period
        self.whole.current_period = self.current_period
        self.plant.current_period = self.current_period

        sheet_ret.write(int(self.current_period), 0, int(self.ret.current_demand))
        sheet_ret.write(int(self.current_period), 1, int(self.ret.inventory))
        sheet_ret.write(int(self.current_period), 2, int(self.distr.inventory))
        sheet_ret.write(int(self.current_period), 3, int(self.whole.inventory))
        sheet_ret.write(int(self.current_period), 4, int(self.plant.inventory_finished))
        sheet_ret.write(int(self.current_period), 5, int(self.plant.inventory_raw))

        self.ret.update()
        self.ret_order = max(self.ret.targetstock - self.ret.inventory, 0)
        #self.ret_order = action[0]

        self.distr.ret_order = self.ret_order
        self.distr.update()
        self.ret.shipment_ret_queue.append((self.distr.shipment, self.current_period))
        self.distr_order = max(self.distr.targetstock - self.distr.inventory, 0)
        #self.distr_order = action[1]

        self.whole.distr_order = self.distr_order
        self.whole.update()
        self.distr.shipment_distr_queue.append((self.whole.shipment, self.current_period))
        self.whole_order = max(self.whole.targetstock - self.whole.inventory, 0)
        #self.whole_order = action[2]

        self.plant.whole_order = self.whole_order
        self.plant.update()
        self.plant.update_costs()
        #self.plant.production = action[3]
        self.plant.production = max(self.plant.targetstock_finished - self.plant.inventory_finished, 0)
        self.plant.produce()
        #self.plant.prod_order = action[4]
        self.plant.prod_order = max(self.plant.targetstock_raw - self.plant.inventory_raw, 0)
        self.plant.plant_order()
        self.whole.shipment_whole_queue.append((self.plant.shipment, self.current_period))

        reward = -(self.ret.periodcosts + self.distr.periodcosts + self.whole.periodcosts + self.plant.periodcosts) / 10000


        sheet_ret.write(int(self.current_period), 6, int(self.ret_order))
        sheet_ret.write(int(self.current_period), 7, int(self.distr_order))
        sheet_ret.write(int(self.current_period), 8, int(self.whole_order))
        sheet_ret.write(int(self.current_period), 9, int(self.plant.production))
        sheet_ret.write(int(self.current_period), 10, int(self.plant.prod_order))

        sheet_ret.write(int(self.current_period), 11, int(self.ret.inventory))
        sheet_ret.write(int(self.current_period), 12, int(self.distr.inventory))
        sheet_ret.write(int(self.current_period), 13, int(self.whole.inventory))
        sheet_ret.write(int(self.current_period), 14, int(self.plant.inventory_finished))
        sheet_ret.write(int(self.current_period), 15, int(self.plant.inventory_raw))

        sheet_ret.write(int(self.current_period), 16, int(self.ret.shipment))
        sheet_ret.write(int(self.current_period), 17, int(self.distr.shipment))
        sheet_ret.write(int(self.current_period), 18, int(self.whole.shipment))
        sheet_ret.write(int(self.current_period), 19, int(self.plant.shipment))
        sheet_ret.write(int(self.current_period), 20, int(self.plant.prod_order))

        sheet_ret.write(int(self.current_period), 21, int(self.ret.periodcosts))
        sheet_ret.write(int(self.current_period), 22, int(self.distr.periodcosts))
        sheet_ret.write(int(self.current_period), 23, int(self.whole.periodcosts))
        sheet_ret.write(int(self.current_period), 24, int(self.plant.periodcosts))

        wb.save(f'xlwt_example{xtime}.xls')

        # print("")
        # print(f"action0: {action[0]}")
        # print(f"action1: {action[1]}")
        # print(f"action2: {action[2]}")
        # print(f"action3: {action[3]}")
        # print(f"ret_inv: {self.ret.inventory}")
        # print(f"ret_inv: {self.distr.inventory}")
        # print(f"whole_inv: {self.whole.inventory}")
        # print(f"plant_inv: {self.plant.inventory_finished}")

        # print(f" ")
        # print(f"total costs: {reward * 10000}")

        if self.current_period >= self.periods:
            done = True
            reward2 = -(self.ret.costs + self.distr.costs + self.whole.costs + self.plant.costs)/10000
            print(f"total costs: {reward2*10000}")
            print(f"ret_sl: {self.ret.sl}")
            print(f"distr_sl: {self.distr.sl}")
            print(f"whole_sl: {self.whole.sl}")
            print(f"plant_sl: {self.plant.sl}")

            # print(f"ret_bl_costs: {self.ret.backlogcosts}")
            # print(f"distr_bl_costs: {self.distr.backlogcosts}")
            # print(f"distr_inv_costs: {self.distr.inventorycosts}")
            # print(f"whole_bl_costs: {self.whole.backlogcosts}")
            # print(f"whole_inv_costs: {self.whole.inventorycosts}")
            # print(f"plant_bl_costs: {self.plant.backlogcosts}")
            # print(f"plant_inv_costs: {self.plant.inventorycosts}")
            # print(f"ret_costs: {self.ret.costs}")
            # print(f"distr_costs: {self.distr.costs}")
            # print(f"whole_costs: {self.whole.costs}")
            # print(f"plant_costs: {self.plant.costs}")
        else:
            done = False
            #reward = 0

        info = {}

        self.state = [self.ret.inventory, self.distr.inventory, self.whole.inventory, self.plant.inventory_raw,
                      self.plant.inventory_finished, self.distr.backlogtotal, self.whole.backlogtotal, self.plant.backlogtotal]
        self.state = np.array(self.state, dtype=np.int32)

        # print(action)
        # print(action[0])
        # print(action[1])
        # print(action[2])
        # print(action[3])


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
        self.plant.inventory_raw = 25
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

        self.ret.targetstock = 15
        self.distr.targetstock = 18
        self.whole.targetstock = 17
        self.plant.targetstock_raw = 18
        self.plant.targetstock_finished = 24

        self.ret.sl = 1
        self.distr.sl = 1
        self.whole.sl = 1
        self.plant.sl = 1

        self.state = [self.ret.inventory, self.distr.inventory, self.whole.inventory, self.plant.inventory_raw,
                      self.plant.inventory_finished, self.distr.backlogtotal, self.whole.backlogtotal, self.plant.backlogtotal]

        self.state = np.array(self.state,dtype=np.int32)

        info = {}

        return self.state, info





