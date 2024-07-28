
# -*- coding: utf-8 -*-

class Retailer:
    def __init__(self, *args, **kwargs):
        self.current_period = 0
        self.current_demand = 0
        self.inventory = 0
        self.leadtimeup = 0
        self.sl = 1.00
        self.costs = 0
        self.backlog = 0
        self.holdingrate = 0
        self.backlograte = 0
        self.backlogcount = 0
        self.backlogtotal = 0
        self.inventorycosts = 0
        self.backlogcosts = 0
        self.shipment = 0
        self.shipment_ret_queue = []
        self.targetstock = 0
        self.periodcosts = 0

    def update(self):
        if self.current_period > 1:
            self.update_inventory_shipment()

        self.update_costs()
        self.update_backlog_and_inventory_demand()
        self.sl = 1 - self.backlogcount / self.current_period

    def update_inventory_shipment(self):
        for row, (shipment, period) in enumerate(self.shipment_ret_queue):
            if int(period) == int(self.current_period) - self.leadtimeup:
                cz = shipment
                break
            else:
                cz = 0
        if len(self.shipment_ret_queue) > 20:
            self.shipment_ret_queue.pop(0)
        self.inventory += int(cz)


    def update_backlog_and_inventory_demand(self):
        if int(self.current_demand) > int(self.inventory):
            self.backlog = int(self.current_demand) - int(self.inventory)
            self.backlogtotal += self.backlog
            self.inventory = 0
        else:
            self.inventory -= int(self.current_demand)
            self.backlog = 0
        if self.backlog > 0:
            self.backlogcount += 1

    def update_costs(self):
        self.inventorycosts += self.inventory * self.holdingrate
        self.backlogcosts = self.backlogtotal * self.backlograte
        self.costs = self.inventorycosts + self.backlogcosts
        self.periodcosts = self.inventory * self.holdingrate + self.backlog * self.backlograte


