#-------------------------------------------------------firm class-------------------------------------------------------------
#imports 
import random as rd 
import numpy as np 

class Firm:
    def __init__(self, t,wage,inventory,price,savings,price_low_lim, price_high_lim, raises, lower):
        self.wage = wage
        self.inventory = inventory
        self.price = price
        self.savings = savings
        self.employees = []
        self.time = t
        self.last_12_months = [self.savings, self.savings, self.savings, self.savings, self.savings, self.savings, self.savings, self.savings, self.savings, self.savings, self.savings, self.savings,]
        self.price_low_lim = price_low_lim
        self.price_high_lim = price_high_lim
        self.raises = raises
        self.lower = lower
    
    def pay_wages(self):
        for employee in self.employees:
            employee.savings += self.wage
            self.savings -= self.wage
    
    def hire(self, person):
        person.employed = True
        person.employer = self
        person.monthlyIncome = self.wage
        self.employees.append(person)
        person.income = self.wage
    
    def fire(self, person):
        person.employed = False
        person.employer = None
        self.employees.remove(person)
        
    def sell_goods(self, quantity):
        revenue = quantity * self.price
        if self.inventory >= quantity:
            self.savings += revenue
            self.inventory -= quantity
        else:
            self.savings += self.inventory * self.price
            self.inventory = 0
        
    def adjust_price(self):
        if self.inventory < self.price_low_lim:
            self.price *= self.raises # 2% up
        elif self.inventory > self.price_high_lim:
            self.price *= self.lower # 2% down
    

    def update(self):
    
        self.last_12_months.append(self.savings)
        self.last_12_months.pop(0)
        
    
        self.pay_wages()
        
     
        old_val = self.last_12_months[0]
        if old_val > 0:
            percentChange = (self.savings - old_val) / old_val
        else:
            percentChange = 0
        
        if percentChange > 0.05:
            self.wage *= 1.01  # Small 1% raise
        elif percentChange < -0.05:
            self.wage *= 0.99  # Small 1% cut
            
        self.adjust_price()
        if self.savings > 500000:
            self.wage *= self.raises     
        if self.savings < 20000: 
            self.wage *= self.lower    
        if self.savings < 0 and len(self.employees) > 0:
            self.fire(rd.choice(self.employees))