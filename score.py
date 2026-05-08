#imports
import numpy as np
import math

#score function
def score(history):
    
    savings = [row["Avg Person Savings"] for row in history]
    if any(math.isnan(s) or math.isinf(s) for s in savings):
        return 0.0
    unemployment = [row["Unemployment Rate"] for row in history]
    firm_savings = [row["Avg Firm Savings"] for row in history]
    
    # monthly returns (percentage change month to month)
    returns = [
        (savings[i] - savings[i-1]) / savings[i-1] 
        for i in range(1, len(savings)) 
        if savings[i-1] > 0
    ]
    
    # sharpe-like score
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    sharpe = mean_return / std_return if std_return > 0 else 0
    sharpe_normalised = np.clip(sharpe, 0, 3) / 3
    
    # employment score
    employment_score = 1 - np.mean(unemployment)
    
    # combined fitness
    firm_health = sum(1 for f in firm_savings if f > 0) / len(firm_savings)
    
    fitness = 0.34 * sharpe_normalised + 0.33 * employment_score + .33 * firm_health
    
    return fitness