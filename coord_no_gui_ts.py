import random
import ret_no_gui
import distr_no_gui
import whole_no_gui
import plant_no_gui

random.seed(10)

ret = ret_no_gui.Retailer()
distr = distr_no_gui.Distributor()
whole = whole_no_gui.Wholesaler()
plant = plant_no_gui.Plant()

ret.holdingrate = 4
ret.backlograte = 40
ret.leadtimeup = 2
ret.inventory = 20

distr.holdingrate = 2
distr.backlograte = 4
distr.leadtimeup = 2
distr.inventory = 20

whole.holdingrate = 2
whole.backlograte = 4
whole.leadtimeup = 2
whole.inventory = 20

plant.holdingrate_raw = 1
plant.holdingrate_finished = 2
plant.backlograte = 4
plant.leadtimeup = 2
plant.inventory_raw = 25
plant.inventory_finished = 20
plant.productiontime = 2

ret.targetstock = 20
distr.targetstock = 20
whole.targetstock = 20
plant.targetstock_raw = 20
plant.targetstock_finished = 20


for rx in range(51):
    if rx > 0:
        current_period = rx
        ret.current_demand = int(random.uniform(8, 12))
        print(" ")
        print(f"current_period: {current_period}")
        ret.current_period = current_period
        distr.current_period = current_period
        whole.current_period = current_period
        plant.current_period = current_period

        print(f"ret_inventory_start: {ret.inventory}")

        print(f"ret_demand: {ret.current_demand}")
        ret.update()

        print(f"ret_inventory_end: {ret.inventory}")
        print(f"ret_backlogtotal: {ret.backlogtotal}")
        print(f"ret_totalcosts: {ret.costs}")
        ret_order = max(ret.targetstock - ret.inventory, 0)
        print(f"ret_order: {ret_order}")

        print(f"distr_inventory_start: {distr.inventory}")
        distr.ret_order = ret_order
        distr.update()

        print(f"distr_inventory_end: {distr.inventory}")
        print(f"distr_backlogtotal: {distr.backlogtotal}")
        print(f"distr_totalcosts: {distr.costs}")

        ret.shipment_ret_queue.append((distr.shipment, current_period))
        distr_order = max(distr.targetstock - distr.inventory, 0)
        print(f"distr_order: {distr_order}")

        print(f"whole_inventory_start: {whole.inventory}")
        whole.distr_order = distr_order
        whole.update()

        print(f"whole_inventory_end: {whole.inventory}")
        print(f"whole_backlogtotal: {whole.backlogtotal}")
        print(f"whole_totalcosts: {whole.costs}")

        distr.shipment_distr_queue.append((whole.shipment, current_period))
        whole_order = max(whole.targetstock - whole.inventory, 0)
        print(f"whole_order: {whole_order}")


        plant.whole_order = whole_order
        plant.update()
        print(f"plant_inventory_raw_start: {plant.inventory_raw}")
        print(f"plant_inventory_finished_start: {plant.inventory_finished}")
        plant.update_costs()
        plant.production = max(plant.targetstock_finished - plant.inventory_finished,0)
        plant.produce()
        plant.prod_order = max(plant.targetstock_raw - plant.inventory_raw, 0)
        plant.plant_order()

        print(f"plant_inventory_raw_end: {plant.inventory_raw}")
        print(f"plant_inventory_finished_end: {plant.inventory_finished}")
        print(f"plant_backlogtotal: {plant.backlogtotal}")
        print(f"plant_totalcosts: {plant.costs}")
        print(f"plant_production: {plant.production }")
        print(f"plant_order: {plant.prod_order}")

        whole.shipment_whole_queue.append((plant.shipment, current_period))

totalcosts = ret.costs + distr.costs + whole.costs + plant.costs
print(f"totalcosts: {totalcosts}")
print(f"ret_sl: {ret.sl}")
print(f"distr_sl: {distr.sl}")
print(f"whole_sl: {whole.sl}")
print(f"plant_sl: {plant.sl}")