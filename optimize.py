#imports 
from main_expriment import main_expriment
from score import score
import cma 


#Optimize function 
def Optimize(num_of_runs):
     
    x0 = [0.75, 10.0, 0.05, 1000, 200, 1500, 1.02, 0.98]
    param_names = ["spendingRate","workRate","bankruptSpendingRate","wage","price_low_lim", "price_high_lim", "raises", "lower"]
    run_counter = [0]
    def fitness_wrapper(x):
        run_counter[0] += 1
        params = dict(zip(param_names, x))
        history = main_expriment(run_counter[0], params, save_output=False)
        return -score(history)
    
    
    if num_of_runs == 0:
        es = cma.CMAEvolutionStrategy(x0, 0.5, {
        'bounds': [
            [0.3, 5.0, 0.01, 500,  50,   500,  1.01, 0.90],
            [1.0, 25.0, 0.15, 3000, 500, 3000, 1.10, 0.99]
        ]
    })
    else:

        es = cma.CMAEvolutionStrategy(x0, 0.5, {
        'maxfevals': num_of_runs,
        'bounds': [
            [0.3, 5.0, 0.01, 500,  50,   500,  1.01, 0.90],  # lower bounds
            [1.0, 25.0, 0.15, 3000, 500, 3000, 1.10, 0.99]   # upper bounds
        ]
        })
    es.optimize(fitness_wrapper)
    best_x = es.result.xbest
    best_params = dict(zip(param_names, best_x))
    return best_params

         
     
