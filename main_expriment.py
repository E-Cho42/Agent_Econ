import pandas as pd
import matplotlib.pyplot as plt
import random as rd
from person import Person
from firm import Firm
from pathlib import Path

def main_expriment(runId):
    # --- INITIALIZATION ---
    
    #person parameters:
    savings = rd.uniform(30000, 80000)
    spendingRate = rd.uniform(0.6, 0.9)
    employed = False
    employer = None 
    workRate = 10
    income = 0
    bankruptSpendingRate = .05
    
    #firm parameters:
    wage = 1000 #np.random.lognormal(mean=10.7, sigma=0.5) / 30  # monthly
    inventory = 1000
    price = rd.uniform(100, 150)
    fsavings = rd.uniform(50000, 200000)
    t = 0
    
    #interesting ones:
    price_low_lim = 200
    price_high_lim = 1500
    lower = .98
    raises = 1.02
    
    
    
    firms = [Firm(t,wage=wage,inventory=inventory,price=price, price_low_lim= price_low_lim, price_high_lim= price_high_lim, lower= lower, raises= raises, savings= fsavings) for _ in range(10)]
    population = [Person(firms=firms, employed= employed, savings= savings, spendingRate= spendingRate, workRate= workRate, income=income, employer= None,bankruptSpendingRate=bankruptSpendingRate ) for _ in range(500)]
    history = [] 

    
    
    # Initial hire
    for person in population:
        employer = rd.choice(firms)
        employer.hire(person)

    # --- SIMULATION ---
    for month in range(1200):
        t += 1
        for firm in firms:
            firm.update()
            
        
        #Rehiring logic
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
        
        #Calculate Metrics
        unemployed_count = sum(1 for p in population if not p.employed)
        avg_savings = sum(p.savings for p in population) / len(population)
        avg_firm_savings = sum(f.savings for f in firms) / len(firms)
        avg_price = sum(f.price for f in firms) / len(firms)
        avg_stock = sum(f.inventory for f in firms) / len(firms)
        avg_wage = sum(f.wage for f in firms) / len(firms)

        #Logging to history list
        history.append({
            "Month": month + 1,
            "Unemployment Rate": unemployed_count / len(population),
            "Avg Person Savings": avg_savings,
            "Avg Firm Savings": avg_firm_savings,
            "Avg Price": avg_price,
            "Avg Inventory": avg_stock,
            "Avg Wage" : avg_wage
        })

        # Optional: Print every 100 months so the console isn't overwhelmed
        if (month + 1) % 100 == 0:
            print(f" Run: { runId} Month {month+1} complete..........................")
            
        # --- VISUALIZATION ---

    df = pd.DataFrame(history)

    # Smaller window (12 months) makes the trend line more sensitive/wiggly
    window_size = 12 
    df['Price_SMA'] = df['Avg Price'].rolling(window=window_size).mean()
    df['Stock_SMA'] = df['Avg Inventory'].rolling(window=window_size).mean()

    # Theme Setup
    plt.rcParams.update({
        "figure.facecolor": "#0d1117", # Dark slate background
        "axes.facecolor": "#0d1117",
        "axes.edgecolor": "#58a6ff",
        "axes.labelcolor": "#c9d1d9",
        "xtick.color": "#c9d1d9",
        "ytick.color": "#c9d1d9",
        "grid.color": "#161b22",
        "text.color": "#c9d1d9"
    })

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharex=True, dpi=100)

    # --- TOP GRAPH: NEON MARKET ---
    ax1.set_title("MARKET RADAR: Price vs. Inventory", fontsize=18, pad=20, color='#00f2ff', fontweight='bold')

    # Price - Neon Blue
    ax1.plot(df["Month"], df["Avg Price"], color='#00f2ff', alpha=0.15, label="_nolegend_")
    ax1.plot(df["Month"], df['Price_SMA'], color='#00f2ff', linewidth=2.5, label=f"Price (SMA {window_size})")
    ax1.set_ylabel("Price ($)", fontsize=12, fontweight='bold', color='#00f2ff')

    # Inventory - Neon Orange
    ax1_twin = ax1.twinx()
    ax1_twin.plot(df["Month"], df["Avg Inventory"], color='#ff9f00', alpha=0.15, label="_nolegend_")
    ax1_twin.plot(df["Month"], df['Stock_SMA'], color='#ff9f00', linewidth=2.5, label=f"Stock (SMA {window_size})")
    ax1_twin.set_ylabel("Inventory Units", fontsize=12, fontweight='bold', color='#ff9f00')
    ax1_twin.grid(False)

    # Combine legends with a dark frame
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left', facecolor='#161b22', edgecolor='#58a6ff')


    # --- BOTTOM GRAPH: NEON ECONOMY ---
    ax2.set_title("SECTOR METRICS: Capital & Labor", fontsize=18, pad=20, color='#ff007f', fontweight='bold')

    # Savings - Neon Green & Purple
    ax2.plot(df["Month"], df["Avg Person Savings"], color='#39ff14', linewidth=2, label="Person Savings", alpha=0.8)
    ax2.plot(df["Month"], df["Avg Firm Savings"], color='#bc13fe', linewidth=2, label="Firm Savings", alpha=0.8)
    ax2.fill_between(df["Month"], df["Avg Person Savings"], color='#39ff14', alpha=0.05)
    ax2.set_ylabel("Capital ($)", fontsize=12, fontweight='bold')

    # Unemployment - Neon Red (Dasher)
    ax2_twin = ax2.twinx()
    ax2_twin.plot(df["Month"], df["Unemployment Rate"], color='#ff3131', linewidth=2, linestyle='--', label="Unemployment Rate")
    ax2_twin.set_ylabel("Unemployment", fontsize=12, fontweight='bold', color='#ff3131')
    ax2_twin.set_ylim(0, 1)
    ax2_twin.grid(False)

    # Combine legends
    lines, labels = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left', facecolor='#161b22', edgecolor='#58a6ff')

    plt.xlabel("Simulation Month", fontsize=12, fontweight='bold', color='#58a6ff')
    plt.tight_layout()

    # 1. Ensure the directory exists
    output_dir = Path("Analysis_Data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2. Define your filename
    # You can use .png, .jpg, or even .pdf
    plot_filename = f"market_radar_analysis_{runId}.png"
    save_path = output_dir / plot_filename

    # 3. Save the figure
    # facecolor=fig.get_facecolor() ensures the dark background isn't saved as white
    plt.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=150)

    print(f"Chart successfully beamed to {save_path}")

    # Optional: Close the plot to free up memory
    plt.close()
    
    # 3. Export to CSV for external deep-dive
    csv_filename = f"simulation_data_{runId}.csv"
    df.to_csv(f"Analysis_Data/{csv_filename}", index=False)
    print(f"\n[SUCCESS] Full raw data exported to: {csv_filename}")
            
    return history
   



        
    
