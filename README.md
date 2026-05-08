# AgentEcon — Agent-Based Computational Economics Simulator

A from-scratch Python implementation of an agent-based economy modeling emergent market dynamics across 500 autonomous citizen agents and 10 competing firms. Built to explore how complex macroeconomic phenomena — inflation, business cycles, wealth inequality, and crisis response — arise from purely local agent interactions with no central coordination.

> *Agent-based computational economics (ACE) is an active research field. This simulator implements core ACE principles: heterogeneous agents, local interaction rules, and emergent global dynamics.*

---

## What It Models

The simulation runs on a monthly timestep. Each month, every agent in the economy makes decisions based only on its own local state — no agent has global knowledge. Macroeconomic patterns emerge from the aggregate of these local decisions.

### The Agents

**Person (500 agents)**

Each citizen has savings, a spending rate drawn from a uniform distribution, a work rate, and an employment status. Every month an employed citizen receives a wage, buys goods from the cheapest firm in a random sample of three (partial price comparison, not perfect information), and contributes inventory to their employer. Unemployed citizens spend a reduced fraction of their savings to survive, injecting money back into the goods market even without income.

```
budget = spendingRate * (income + 0.05 * savings)
units_to_buy = floor(budget / firm.price)
```

**Firm (10 agents)**

Each firm tracks savings, inventory, a wage level, a price, and an employee list. Every month a firm pays wages to all employees, adjusts its wage up or down based on 12-month rolling profit trend, adjusts its price based on inventory levels, and fires a random employee if savings go negative. Firms hire from the unemployed pool when savings exceed a threshold.

Price adjustment follows a bounded inventory signal:

```
if inventory < price_low_lim:  price *= raises   # low stock → raise price
if inventory > price_high_lim: price *= lower     # high stock → lower price
```

Wage adjustment follows a rolling performance signal:

```
percentChange = (savings_now - savings_12mo_ago) / savings_12mo_ago
if percentChange > 0.05:  wage *= 1.01   # profitable → small raise
if percentChange < -0.05: wage *= 0.99   # losing money → small cut
```

---

## Emergent Phenomena

None of the following were explicitly programmed. They emerge from the local agent rules described above.

**Endogenous Inflation**

Wages rise when firms are profitable. Higher wages raise firm costs. Firms raise prices to compensate. This wage-price spiral produces a slow upward drift in the price level over hundreds of months — a model of demand-pull inflation arising from purely local incentives.

**Price Discovery and Inventory Cycles**

The price-inventory relationship produces oscillating business cycles visible in the output charts. Low inventory triggers price increases, which reduces demand, which allows inventory to recover, which triggers price decreases — a cobweb-style cycle that stabilizes into a fluctuating equilibrium.

**Capital Accumulation Asymmetry**

Firms receive purchases from all 500 citizens but only pay wages to their own ~50 employees. Over time firm savings grow relative to person savings, producing a structural wealth gap between capital and labor without any explicit inequality mechanism.

---

## Stochastic Macro Events

The simulation includes 13 probabilistic macro events drawn each month from a Bernoulli process. Events have a defined probability of triggering, a duration, and symmetric start/end effects that modify agent state variables directly.

| Event | Probability | Duration | Effect |
|-------|-------------|----------|--------|
| Pandemic | 0.05%/mo | 12 months | Spending ×0.5, workRate ×0.6 |
| Recession | 0.08%/mo | 18 months | Spending ×0.6, wages ×0.9 |
| Government Stimulus | 0.03%/mo | 1 month | +$5,000 to every citizen |
| Progressive Tax | 0.05%/mo | 1 month | 5% of firm savings redistributed equally |
| Inflation Shock | 0.04%/mo | 1 month | All prices ×1.20 (sticky — does not reverse) |
| Supply Chain Disruption | 0.05%/mo | 6 months | workRate ×0.5 |
| Investment Boom | 0.04%/mo | 1 month | All firm savings ×1.10 |
| Credit Crunch | 0.03%/mo | 6 months | Immediate layoffs at firms with savings < $10,000 |
| Trade War | 0.04%/mo | 12 months | Spending ×0.8, prices ×1.10 |
| Bankruptcy Cascade | 0.02%/mo | 1 month | Weakest firm collapses, contagion spreads to others |
| Population Growth | 0.03%/mo | 1 month | 50 new citizens added with lower initial savings |
| Productivity Revolution | 0.02%/mo | 1 month | workRate ×1.5 (permanent) |
| Hyperinflation | 0.01%/mo | 6 months | All prices ×2.0, price dynamics more volatile (sticky) |

Note: inflation shock and hyperinflation are intentionally irreversible — prices do not snap back at event end, modeling the real-world stickiness of inflation.

Events are logged to the output CSV and shaded on the output charts for visual analysis.

---

## Parameter Optimization via CMA-ES

Initial conditions are calibrated using **Covariance Matrix Adaptation Evolution Strategy (CMA-ES)**, an industry-standard black-box optimization algorithm used in quantitative finance for strategy calibration and hyperparameter search.

### Why CMA-ES

CMA-ES maintains a multivariate Gaussian distribution over the parameter space. Each generation it samples candidate parameter sets, evaluates their fitness, and updates both the distribution mean and covariance matrix to sample more densely near high-performing regions. The covariance adaptation means the algorithm learns correlations between parameters — for example, that high `workRate` and high `wage` tend to interact well — and exploits those relationships in subsequent generations.

This makes CMA-ES significantly more sample-efficient than grid search or random search, which matters when each evaluation requires running a full 1200-month simulation.

### Fitness Function

The fitness function rewards three properties simultaneously:

```python
fitness = 0.4 * sharpe_score + 0.3 * employment_score + 0.3 * firm_health
```

**Sharpe-like score** — computed from the monthly return series of average person savings:

```python
returns = [(savings[i] - savings[i-1]) / savings[i-1] for i in range(1, len(savings))]
sharpe = mean(returns) / std(returns)
sharpe_normalised = clip(sharpe, 0, 3) / 3
```

This directly mirrors the Sharpe ratio from quantitative finance — it rewards economies that grow *consistently*, not ones that spike and crash. A high mean return with low volatility scores highly; a volatile run-up followed by collapse scores poorly even if the terminal value is the same.

**Employment score** — average employment rate across all 1200 months:

```python
employment_score = 1 - mean(unemployment_rate)
```

**Firm health** — fraction of months in which average firm savings remained positive:

```python
firm_health = sum(1 for f in firm_savings if f > 0) / len(firm_savings)
```

This penalises parameter combinations that produce high household wealth at the cost of insolvent firms — an unstable equilibrium that would eventually collapse.

### Parameters Searched

| Parameter | Bounds | Description |
|-----------|--------|-------------|
| `spendingRate` | [0.3, 1.0] | Fraction of income+savings spent monthly |
| `workRate` | [5.0, 25.0] | Units of inventory produced per worker per month |
| `bankruptSpendingRate` | [0.01, 0.15] | Spending rate when unemployed |
| `wage` | [500, 3000] | Starting monthly wage |
| `price_low_lim` | [50, 500] | Inventory threshold below which price rises |
| `price_high_lim` | [500, 3000] | Inventory threshold above which price falls |
| `raises` | [1.01, 1.10] | Price/wage increase multiplier |
| `lower` | [0.90, 0.99] | Price/wage decrease multiplier |

Starting savings and firm savings are excluded from the search — they are randomised at initialisation and their mean adds noise without informing structural behaviour.

### Running the Optimizer

```bash
pip install cma
python main.py
```

`main.py` calls `Optimize()` first, which runs ~200 CMA-ES evaluations to find the best parameter set, then runs a single final simulation with those parameters and `save_output=True` to produce the analysis chart and CSV.

---

## Output and Analysis

Each simulation run produces two files in `Analysis_Data/`:

**Chart (`market_radar_analysis_{runId}.png`)** — two-panel visualization showing price and inventory dynamics (top) with 12-month SMA smoothing, and capital/labor metrics with unemployment and event shading (bottom).

**CSV (`simulation_data_{runId}.csv`)** — full monthly time series including unemployment rate, average person savings, average firm savings, average price, average inventory, average wage, and active event name. Suitable for external statistical analysis.

---

## Architecture

```
AgentEcon/
├── main.py               # Entry point — runs optimizer then final simulation
├── main_expriment.py     # Simulation loop, metrics logging, visualization
├── optimize.py           # CMA-ES parameter optimizer
├── score.py              # Fitness function (Sharpe + employment + firm health)
├── person.py             # Person agent class
├── firm.py               # Firm agent class
├── Event.py              # Event class and all macro event definitions
└── Analysis_Data/        # Output directory for charts and CSVs
```

**`optimize.py`** — Wraps `main_expriment` and `score` in a CMA-ES optimization loop. Searches the parameter space across ~200 evaluations with explicit bounds to prevent numerical overflow. Returns the best parameter dict found.

**`score.py`** — Computes a scalar fitness value from a simulation history. Implements a Sharpe-like return quality metric, an employment score, and a firm solvency health score, combined with weighted averaging.

**`person.py`** — Agent with savings, spendingRate, workRate, income, and employment status. Implements partial price comparison (samples 3 firms, buys from cheapest), inventory contribution via `go_to_work()`, and reduced survival spending when unemployed.

**`firm.py`** — Agent with savings, inventory, price, wage, and employee list. Implements 12-month rolling profit-based wage adjustment, inventory-signal price adjustment with configurable bounds, and bankruptcy-triggered firing.

**`Event.py`** — Event system with probabilistic monthly trigger (`roll()`), duration countdown (`tick()`), and symmetric start/end effect functions. All 13 macro events defined as instances of the `Event` class.

**`main_expriment.py`** — Simulation loop running 1200 months per trial. Accepts a `params` dict and a `save_output` flag. Handles initial hiring, monthly firm and person updates, rehiring logic, event rolling and ticking, metrics calculation, and optional chart/CSV output.

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `N_POPULATION` | 500 | Number of citizen agents |
| `N_FIRMS` | 10 | Number of firm agents |
| `MONTHS` | 1200 | Simulation duration |
| `wage` | 1000 | Starting monthly wage |
| `price` | Uniform(100, 150) | Starting goods price |
| `price_low_lim` | 200 | Inventory threshold below which price rises |
| `price_high_lim` | 1500 | Inventory threshold above which price falls |
| `raises` | 1.02 | Price/wage increase multiplier |
| `lower` | 0.98 | Price/wage decrease multiplier |
| `bankruptSpendingRate` | 0.05 | Fraction of savings spent monthly when unemployed |

---

## Installation

Requires Python 3.x

```bash
pip install numpy pandas matplotlib cma
python main.py
```

---

## Theoretical Grounding

The model draws on several established frameworks in computational economics. The price adjustment mechanism is analogous to the cobweb model of supply and demand dynamics. The wage-price spiral mirrors cost-push and demand-pull inflation theory. The emergent wealth gap between firm and household savings reflects the classical Marxian distinction between capital accumulation and wage labor. The stochastic event system follows a Poisson process — each event has a fixed per-period probability of occurrence independent of history.

The fitness function used for parameter optimization is directly analogous to risk-adjusted return metrics in quantitative finance. The Sharpe ratio component measures return quality rather than raw magnitude, penalising volatile growth paths in the same way a portfolio manager would prefer steady compounding over high-variance speculation.