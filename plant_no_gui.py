
# -*- coding: utf-8 -*-

class Plant:

    def __init__(self, *args, **kwargs):
        self.shipment_plant_queue = []
        self.production_plant_queue = []
        self.supplier_order = 0
        self.produced_lot = 0
        self.current_period = 0
        self.current_demand = 0
        self.inventory_raw = 0
        self.inventory_finished = 0
        self.leadtimeup = 2
        self.sl = 1.00
        self.costs = 0
        self.backlog = 0
        self.backlogtotal = 0
        self.holdingrate_raw = 0
        self.holdingrate_finished = 0
        self.backlograte = 0
        self.backlogcount = 0
        self.productiontime = 0
        #self.prodshipmentList = []
        self.backlogcosts = 0
        self.inventorycosts = 0
        self.whole_order = 0
        self.shipment = 0
        self.production = 0
        self.prod_order = 0
        self.targetstock_raw = 0
        self.targetstock_finished = 0
        self.periodcosts = 0

    def update(self):
        self.current_demand = self.whole_order
        self.supplier_order = next((
            int(row[0]) for row in self.shipment_plant_queue if int(row[1]) == self.current_period - self.leadtimeup
        ), 0)

        self.inventory_raw += self.supplier_order

        if len(self.shipment_plant_queue) > 20:
            self.shipment_plant_queue.pop(0)

        self.produced_lot = next((
            int(row[0]) for row in self.production_plant_queue if int(row[1]) == self.current_period
        ), 0)

        if len(self.production_plant_queue) > 20:
            self.production_plant_queue.pop(0)

        self.inventory_finished += self.produced_lot
        #self.update_costs()

    def update_costs(self):
        self.inventorycosts += self.inventory_raw * self.holdingrate_raw + self.inventory_finished * self.holdingrate_finished
        self.backlogcosts += self.backlogtotal * self.backlograte
        self.costs = self.inventorycosts + self.backlogcosts
        self.periodcosts = self.inventory_raw * self.holdingrate_raw + self.inventory_finished * self.holdingrate_finished + self.backlogtotal * self.backlograte
        self.update_backlog_and_inventory_demand()
        self.sl = 1 - self.backlogcount / self.current_period

    def produce(self):
        #self.production = max(self.targetstock_finished - self.inventory_finished,0)
        self.production = min(self.production, int(self.inventory_raw))
        self.inventory_raw -= self.production
        self.production_plant_queue.append([self.production, self.current_period + self.productiontime])

    def update_backlog_and_inventory_demand(self):
        self.shipment = min(self.inventory_finished, self.backlogtotal + self.current_demand)
        self.backlogtotal += self.current_demand - self.shipment
        if int(self.current_demand) > int(self.shipment):
            #self.backlog = int(self.current_demand) - int(self.shipment)
            self.backlogcount += 1
            self.inventory_finished = 0
        else:
            self.inventory_finished += - int(self.shipment)

    def plant_order(self):
            #self.prod_order = max(self.targetstock_raw - self.inventory_raw, 0)
            self.shipment_plant_queue.append((self.prod_order, self.current_period))



