import pandas as pd
import matplotlib.pyplot as plt
import random as rd
from person import Person
from firm import Firm
from pathlib import Path
from Event import Event, create_events

def main_expriment(runId, multiplier):
    # --- INITIALIZATION ---
    #person parameters:
    savings = rd.uniform(30000, 80000)  * multiplier 
    spendingRate = rd.uniform(0.6, 0.9) * multiplier
    employed = False
    employer = None 
    workRate = 10 *  multiplier
    income = 0
    bankruptSpendingRate = .05 *  multiplier
    
    #firm parameters:
    wage = 1000 * multiplier
    inventory = 1000 * multiplier
    price = rd.uniform(100, 150) *multiplier
    fsavings = rd.uniform(50000, 200000) *  multiplier
    t = 0
    
    #interesting ones:
    price_low_lim = 200 *  multiplier
    price_high_lim = 1500 * multiplier
    lower = .98 *  multiplier
    raises = 1.02 *  multiplier
    
    firms = [Firm(t, wage=wage, inventory=inventory, price=price, price_low_lim=price_low_lim, price_high_lim=price_high_lim, lower=lower, raises=raises, savings=fsavings) for _ in range(10)]
    population = [Person(firms=firms, employed=employed, savings=savings, spendingRate=spendingRate, workRate=workRate, income=income, employer=None, bankruptSpendingRate=bankruptSpendingRate) for _ in range(500)]
    history = []

    # initialize events after population and firms exist
    events = create_events()

    # Initial hire
    for person in population:
        employer = rd.choice(firms)
        employer.hire(person)

    # --- SIMULATION ---
    for month in range(1200):
        t += 1
        for firm in firms:
            firm.update()
            
        # Rehiring logic
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

        #roll and tick all events each month
        for event in events:
            event.roll(population, firms)
            event.tick(population, firms)

        #track which event is active for logging
        active_event = next((e.name for e in events if e.active), "None")

        # Calculate Metrics
        unemployed_count = sum(1 for p in population if not p.employed)
        avg_savings = sum(p.savings for p in population) / len(population)
        avg_firm_savings = sum(f.savings for f in firms) / len(firms)
        avg_price = sum(f.price for f in firms) / len(firms)
        avg_stock = sum(f.inventory for f in firms) / len(firms)
        avg_wage = sum(f.wage for f in firms) / len(firms)

        # Logging to history list
        history.append({
            "Month": month + 1,
            "Active Event": active_event,  
            "Unemployment Rate": unemployed_count / len(population),
            "Avg Person Savings": avg_savings,
            "Avg Firm Savings": avg_firm_savings,
            "Avg Price": avg_price,
            "Avg Inventory": avg_stock,
            "Avg Wage": avg_wage
        })

        if (month + 1) % 100 == 0:
            print(f"Run: {runId} Month {month+1} | Event: {active_event}")  

    df = pd.DataFrame(history)

    window_size = 12 
    df['Price_SMA'] = df['Avg Price'].rolling(window=window_size).mean()
    df['Stock_SMA'] = df['Avg Inventory'].rolling(window=window_size).mean()

    plt.rcParams.update({
        "figure.facecolor": "#0d1117",
        "axes.facecolor": "#0d1117",
        "axes.edgecolor": "#58a6ff",
        "axes.labelcolor": "#c9d1d9",
        "xtick.color": "#c9d1d9",
        "ytick.color": "#c9d1d9",
        "grid.color": "#161b22",
        "text.color": "#c9d1d9"
    })

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharex=True, dpi=100)

    ax1.set_title("MARKET RADAR: Price vs. Inventory", fontsize=18, pad=20, color='#00f2ff', fontweight='bold')
    ax1.plot(df["Month"], df["Avg Price"], color='#00f2ff', alpha=0.15, label="_nolegend_")
    ax1.plot(df["Month"], df['Price_SMA'], color='#00f2ff', linewidth=2.5, label=f"Price (SMA {window_size})")
    ax1.set_ylabel("Price ($)", fontsize=12, fontweight='bold', color='#00f2ff')

    ax1_twin = ax1.twinx()
    ax1_twin.plot(df["Month"], df["Avg Inventory"], color='#ff9f00', alpha=0.15, label="_nolegend_")
    ax1_twin.plot(df["Month"], df['Stock_SMA'], color='#ff9f00', linewidth=2.5, label=f"Stock (SMA {window_size})")
    ax1_twin.set_ylabel("Inventory Units", fontsize=12, fontweight='bold', color='#ff9f00')
    ax1_twin.grid(False)

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left', facecolor='#161b22', edgecolor='#58a6ff')

    ax2.set_title("SECTOR METRICS: Capital & Labor", fontsize=18, pad=20, color='#ff007f', fontweight='bold')
    ax2.plot(df["Month"], df["Avg Person Savings"], color='#39ff14', linewidth=2, label="Person Savings", alpha=0.8)
    ax2.plot(df["Month"], df["Avg Firm Savings"], color='#bc13fe', linewidth=2, label="Firm Savings", alpha=0.8)
    ax2.fill_between(df["Month"], df["Avg Person Savings"], color='#39ff14', alpha=0.05)
    ax2.set_ylabel("Capital ($)", fontsize=12, fontweight='bold')

    #shade regions where events are active
    event_colors = {
    "Pandemic": "#ff000044",
    "Recession": "#ff660044",
    "Government Stimulus": "#00ff0044",
    "Progressive Tax": "#ffff0044",
    "Inflation Shock": "#ff99ff44",
    "Supply Chain Disruption": "#ff990044",
    "Investment Boom": "#00ffff44",
    "Credit Crunch": "#ff000088",
    "Trade War": "#ff440044",
    "Bankruptcy Cascade": "#ff000099",
    "Population Growth": "#00ff9944",
    "Productivity Revolution": "#ffffff44",
    "Hyperinflation": "#ff000066",
}
    for event_name, color in event_colors.items():
        event_months = df[df["Active Event"] == event_name]["Month"]
        if not event_months.empty:
            ax2.axvspan(event_months.min(), event_months.max(), color=color, label=event_name)

    ax2_twin = ax2.twinx()
    ax2_twin.plot(df["Month"], df["Unemployment Rate"], color='#ff3131', linewidth=2, linestyle='--', label="Unemployment Rate")
    ax2_twin.set_ylabel("Unemployment", fontsize=12, fontweight='bold', color='#ff3131')
    ax2_twin.set_ylim(0, 1)
    ax2_twin.grid(False)

    lines, labels = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left', facecolor='#161b22', edgecolor='#58a6ff')

    plt.xlabel("Simulation Month", fontsize=12, fontweight='bold', color='#58a6ff')
    plt.tight_layout()

    output_dir = Path("Analysis_Data")
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_filename = f"market_radar_analysis_{runId}.png"
    save_path = output_dir / plot_filename
    plt.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=150)
    print(f"Chart successfully beamed to {save_path}")
    plt.close()
    
    csv_filename = f"simulation_data_{runId}.csv"
    df.to_csv(f"Analysis_Data/{csv_filename}", index=False)
    print(f"\n[SUCCESS] Full raw data exported to: {csv_filename}")
            
    return history

