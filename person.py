#-------------------------------------------------------person class-------------------------------------------------------------
#imports:
import random as rd 
import numpy as np

#person class
class Person():
    def __init__(self, firms,savings, spendingRate, employed, employer, workRate, income, bankruptSpendingRate):
        self.savings = savings #rd.uniform(30000, 80000)
        self.spendingRate = spendingRate #rd.uniform(0.6, 0.9)
        self.employed = employed #False
        self.employer = employer 
        self.firms = firms
        self.workRate = workRate #10
        self.income = income #0
        self.bankruptSpendingRate = bankruptSpendingRate

    def buy_goods(self):
        # Pick 3 random firms and choose the cheapest among them 
        potential_firms = rd.sample(self.firms, min(3, len(self.firms)))
        firm = min(potential_firms, key=lambda f: f.price)
        
        budget = self.spendingRate * (self.income + 0.05 * self.savings) 
        if firm.price <= 0 or budget <= 0:
            return
        
        units_to_buy = int(budget // firm.price)
        
        if units_to_buy > 0 and firm.inventory > 0:
            actual_units = min(units_to_buy, firm.inventory)
            cost = actual_units * firm.price
            
            firm.savings += cost
            self.savings -= cost
            firm.inventory -= actual_units
            
    def go_to_work(self):
        # Only work if employer still exists (safety check)
        if self.employer:
            self.employer.inventory += self.workRate
        
    def update(self):
        if self.savings <= 0: return # Stop if bankrupt

        if self.employed:
            self.buy_goods()
            self.go_to_work()
        else:
            spend = self.savings * self.bankruptSpendingRate
            firm = rd.choice(self.firms)
            
            units = int(spend // firm.price) if firm.price > 0 else 0
            if units > 0 and firm.inventory > 0:
                actual = min(units, firm.inventory)
                cost = actual * firm.price
                firm.savings += cost
                self.savings -= cost
                firm.inventory -= actual

    def is_bankrupt(self):
        return self.savings <= 0