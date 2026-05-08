#imports 
from main_expriment import main_expriment
from optimize import Optimize

if __name__ == "__main__":
    
    best_params = Optimize(num_of_runs = 0)
    
    
    
    for i in range(50):
        main_expriment(i, best_params, save_output= True)

    print(best_params)
        
    
        