from person import Person
from firm import Firm
import random as rd

# create agents
firms = [Firm() for _ in range(10)]
population = [Person(firms=firms) for _ in range(500)]

# assign people to firms
for person in population:
    employer = rd.choice(firms)
    employer.hire(person)

# run simulation
for month in range(10000):
    for firm in firms:
        firm.update()
    
    # rehiring — profitable firms hire unemployed people
    unemployed = [p for p in population if not p.employed]
    for firm in firms:
        if firm.savings > 50000 and unemployed:
            hires = min(3, len(unemployed))
            for _ in range(hires):
                if unemployed:
                    person = rd.choice(unemployed)
                    firm.hire(person)
                    unemployed.remove(person)
    
    for person in population:
        person.update()
    
    # metrics
    unemployed_count = sum(1 for p in population if not p.employed)
    avg_savings = sum(p.savings for p in population) / len(population)
    avg_firm_savings = sum(f.savings for f in firms) / len(firms)
    total_money = sum(p.savings for p in population) + sum(f.savings for f in firms)
    avg_price = sum(f.price for f in firms) / len(firms)
    avg_stock = sum(f.inventory for  f in firms)/ len(firms)

    print(f"Month {month+1}: avg savings = ${avg_savings:.2f} | unemployed = {unemployed_count} | avg firm savings = ${avg_firm_savings:.2f}| avg price = ${avg_price}| avg stock = {avg_stock}")