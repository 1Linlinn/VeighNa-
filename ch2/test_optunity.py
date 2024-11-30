import optunity
import numpy as np
import matplotlib.pyplot as plt

def func(x):
    """ 待优化的函数 """
    return (np.sin(x) + 2) * x ** 2

x_range = [-100, 100]
xs = list(range(*x_range))
ys = [func(i) for i in xs]

# 绘制待优化函数图像
plt.plot(xs, ys)
plt.show()

opt = optunity.minimize(func, num_evals=500, solver_name='particle swarm', x=x_range)
opt_params, details, suggestion = opt
print(opt_params)
print(details)
print(suggestion)
