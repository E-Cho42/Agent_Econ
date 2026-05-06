#-------------------------------------------------------event class-------------------------------------------------------------
#imports 
import random as rd 
import numpy as np

# Event Class
class Event:
    def __init__(self, name, probability, duration, effect_fn, description):
        self.name = name
        self.probability = probability
        self.duration = duration
        self.effect_fn = effect_fn
        self.description = description
        self.active = False
        self.months_remaining = 0
    
    def trigger(self, population, firms):
        self.active = True
        self.months_remaining = self.duration
        self.effect_fn(population, firms, "start")
    
    def tick(self, population, firms):
        if self.active:
            self.months_remaining -= 1
            if self.months_remaining <= 0:
                self.active = False
                self.effect_fn(population, firms, "end")
    
    def roll(self, population, firms):
        if not self.active:
            if rd.random() < self.probability:
                self.trigger(population, firms)


# -----------------------------------------------------------
# TIER 1 EVENTS
# -----------------------------------------------------------

def pandemic_effect(population, firms, phase):
    if phase == "start":
        for p in population:
            p.spendingRate *= 0.5
            p.workRate *= 0.6
    elif phase == "end":
        for p in population:
            p.spendingRate /= 0.5
            p.workRate /= 0.6

pandemic = Event(
    name="Pandemic",
    probability=0.002,
    duration=12,
    effect_fn=pandemic_effect,
    description="A global pandemic crashes spending and productivity"
)

def recession_effect(population, firms, phase):
    if phase == "start":
        for p in population:
            p.spendingRate *= 0.6
        for f in firms:
            f.wage *= 0.9
    elif phase == "end":
        for p in population:
            p.spendingRate /= 0.6
        for f in firms:
            f.wage /= 0.9

recession = Event(
    name="Recession",
    probability=0.003,
    duration=18,
    effect_fn=recession_effect,
    description="Consumer confidence collapses, spending drops and wages are cut"
)

def stimulus_effect(population, firms, phase):
    if phase == "start":
        for p in population:
            p.savings += 5000

stimulus = Event(
    name="Government Stimulus",
    probability=0.001,
    duration=1,
    effect_fn=stimulus_effect,
    description="Government sends every citizen a one-time $5000 payment"
)

def tax_effect(population, firms, phase):
    if phase == "start":
        total_collected = 0
        for f in firms:
            tax = f.savings * 0.05
            f.savings -= tax
            total_collected += tax
        payment = total_collected / len(population)
        for p in population:
            p.savings += payment

tax = Event(
    name="Progressive Tax",
    probability=0.002,
    duration=1,
    effect_fn=tax_effect,
    description="5% of firm savings redistributed equally to all citizens"
)

# -----------------------------------------------------------
# TIER 2 EVENTS
# -----------------------------------------------------------

def inflation_shock_effect(population, firms, phase):
    if phase == "start":
        for f in firms:
            f.price *= 1.20  # prices jump 20% overnight
    elif phase == "end":
        pass  # prices don't snap back — inflation is sticky

inflation_shock = Event(
    name="Inflation Shock",
    probability=0.002,
    duration=1,
    effect_fn=inflation_shock_effect,
    description="A sudden inflation shock drives all prices up 20%"
)

def supply_chain_effect(population, firms, phase):
    if phase == "start":
        for p in population:
            p.workRate *= 0.5  # workers produce less
    elif phase == "end":
        for p in population:
            p.workRate /= 0.5

supply_chain = Event(
    name="Supply Chain Disruption",
    probability=0.003,
    duration=6,
    effect_fn=supply_chain_effect,
    description="Global supply chain disruption halves worker productivity for 6 months"
)

def investment_boom_effect(population, firms, phase):
    if phase == "start":
        for f in firms:
            f.savings *= 1.10  # 10% outside capital injection

investment_boom = Event(
    name="Investment Boom",
    probability=0.002,
    duration=1,
    effect_fn=investment_boom_effect,
    description="Outside investors inject capital — all firm savings rise 10%"
)

def credit_crunch_effect(population, firms, phase):
    if phase == "start":
        # fire all employees at firms that are already close to broke
        for f in firms:
            if f.savings < 10000:
                for employee in list(f.employees):
                    f.fire(employee)
    elif phase == "end":
        pass  # recovery handled by normal rehiring logic

credit_crunch = Event(
    name="Credit Crunch",
    probability=0.002,
    duration=6,
    effect_fn=credit_crunch_effect,
    description="Credit dries up — financially weak firms must immediately lay off workers"
)

def trade_war_effect(population, firms, phase):
    if phase == "start":
        for p in population:
            p.spendingRate *= 0.8  # consumers tighten belts
        for f in firms:
            f.price *= 1.10  # domestic prices rise due to tariffs
    elif phase == "end":
        for p in population:
            p.spendingRate /= 0.8
        for f in firms:
            f.price /= 1.10

trade_war = Event(
    name="Trade War",
    probability=0.002,
    duration=12,
    effect_fn=trade_war_effect,
    description="Trade war drives up domestic prices and dampens consumer spending"
)

# -----------------------------------------------------------
# TIER 3 EVENTS
# -----------------------------------------------------------

def bankruptcy_cascade_effect(population, firms, phase):
    if phase == "start":
        # find the weakest firm and collapse it
        weakest = min(firms, key=lambda f: f.savings)
        cascade_loss = weakest.savings * 0.3
        weakest.savings = 0
        # fire all its employees
        for employee in list(weakest.employees):
            weakest.fire(employee)
        # spread contagion to other firms
        for f in firms:
            if f != weakest:
                f.savings -= cascade_loss * 0.2

bankruptcy_cascade = Event(
    name="Bankruptcy Cascade",
    probability=0.001,
    duration=1,
    effect_fn=bankruptcy_cascade_effect,
    description="The weakest firm collapses, sending shockwaves through the economy"
)

def population_growth_effect(population, firms, phase):
    if phase == "start":
        # add 50 new people — note: modifies list in place
        new_people = [
            type(population[0])(
                firms=population[0].firms,
                employed=False,
                savings=rd.uniform(5000, 20000),  # new arrivals start poorer
                spendingRate=rd.uniform(0.6, 0.9),
                workRate=10,
                income=0,
                employer=None,
                bankruptSpendingRate=0.05
            ) for _ in range(50)
        ]
        population.extend(new_people)

population_growth = Event(
    name="Population Growth",
    probability=0.002,
    duration=1,
    effect_fn=population_growth_effect,
    description="50 new citizens arrive in the economy, starting with modest savings"
)

def productivity_revolution_effect(population, firms, phase):
    if phase == "start":
        for p in population:
            p.workRate *= 1.5  # permanent productivity boost
    # no end phase — the revolution is permanent

productivity_revolution = Event(
    name="Productivity Revolution",
    probability=0.001,
    duration=1,
    effect_fn=productivity_revolution_effect,
    description="A technological breakthrough permanently raises worker productivity by 50%"
)

def hyperinflation_effect(population, firms, phase):
    if phase == "start":
        for f in firms:
            f.price *= 2.0
            f.raises *= 1.05  # price adjustment becomes more aggressive
            f.lower *= 0.95
    elif phase == "end":
        for f in firms:
            f.raises /= 1.05
            f.lower /= 0.95
        # prices stay high — hyperinflation doesn't reverse

hyperinflation = Event(
    name="Hyperinflation",
    probability=0.001,
    duration=6,
    effect_fn=hyperinflation_effect,
    description="Runaway inflation doubles all prices and makes price dynamics more volatile"
)


# -----------------------------------------------------------
# CREATE EVENTS LIST
# -----------------------------------------------------------

def create_events():
    return [
        # Tier 1 — serious but occasional
        Event("Pandemic", 0.0005, 12, pandemic_effect, "A global pandemic crashes spending and productivity"),
        Event("Recession", 0.0008, 18, recession_effect, "Consumer confidence collapses, spending drops and wages are cut"),
        Event("Government Stimulus", 0.0003, 1, stimulus_effect, "Government sends every citizen a one-time $5000 payment"),
        Event("Progressive Tax", 0.0005, 1, tax_effect, "5% of firm savings redistributed equally to all citizens"),
        
        # Tier 2 — rare disruptions
        Event("Inflation Shock", 0.0004, 1, inflation_shock_effect, "A sudden inflation shock drives all prices up 20%"),
        Event("Supply Chain Disruption", 0.0005, 6, supply_chain_effect, "Global supply chain disruption halves worker productivity"),
        Event("Investment Boom", 0.0004, 1, investment_boom_effect, "Outside investors inject capital into all firms"),
        Event("Credit Crunch", 0.0003, 6, credit_crunch_effect, "Credit dries up — weak firms must immediately lay off workers"),
        Event("Trade War", 0.0004, 12, trade_war_effect, "Trade war drives up domestic prices and dampens spending"),
        
        # Tier 3 — very rare, high impact
        Event("Bankruptcy Cascade", 0.0002, 1, bankruptcy_cascade_effect, "The weakest firm collapses sending shockwaves through the economy"),
        Event("Population Growth", 0.0003, 1, population_growth_effect, "50 new citizens arrive in the economy"),
        Event("Productivity Revolution", 0.0002, 1, productivity_revolution_effect, "A breakthrough permanently raises worker productivity"),
        Event("Hyperinflation", 0.0001, 6, hyperinflation_effect, "Runaway inflation doubles all prices"),
    ]