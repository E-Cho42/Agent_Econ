#-------------------------------------------------------firm class-------------------------------------------------------------
#imports 
import random as rd 
import numpy as np 

class Firm:
    def __init__(self):
        self.wage = 1000 #np.random.lognormal(mean=10.7, sigma=0.5) / 12  # monthly
        self.inventory = 1000
        self.price = rd.uniform(100, 150)
        self.savings = rd.uniform(500000, 2000000)
        self.employees = []
    
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
            # Sell what is left
            self.savings += self.inventory * self.price
            self.inventory = 0
        
    def adjust_price(self):
        if self.inventory < 500:
            self.price *= 1.02 # 2% up
        elif self.inventory > 1500:
            self.price *= 0.98 # 2% down
    
    
    def update(self):
        # 1. Pay wages first
        self.pay_wages()
        
        # 2. Adjust price based on demand (inventory levels)
        self.adjust_price()
        
        # 3. Bankruptcy logic: Only fire if savings are dangerously low
        # and maybe try lowering wages before firing?
        if self.savings < self.wage * 2: # Less than 2 months of payroll
            if self.employees:
                self.fire(rd.choice(self.employees))