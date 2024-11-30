import optuna
import numpy as np

def func(x):
    """ 待优化的函数 """
    return (np.sin(x) + 2) * x ** 2

def objective(trial):
    x_range = trial.suggest_uniform('x', -100, 100)
    return func(x_range)

study = optuna.create_study()
study.optimize(objective, n_trials=500)
print(study.best_params)
