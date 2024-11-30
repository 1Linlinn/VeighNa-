import numpy as np

def f(x):
    """ 生成随机序列的函数 """
    return np.sin(x) + np.random.rand(*x.shape) - 0.5

import matplotlib.pyplot as plt

np.random.seed(1234)
# 一共生成50个训练数据样本
x = np.linspace(-10, 10, 50)
y = f(x)
plt.plot(x, y)
plt.show()

# 用于当前值的前两个值作为训练数据
# 一共使用前44个数作为训练数据(最开始两个数没有训练数据,则忽略)
train_y = np.transpose(np.stack([y[: 43], y[1: 44]]))
label_y = y[2: 45]

from sklearn.svm import SVR
import pandas as pd

svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
# 模型拟合训练数据
svr_rbf.fit(train_y, label_y)

# 预测数据的第一个标签为原序列中的第45个数
# 因此训练数据从第43和第44个数开始
predicts = svr_rbf.predict(np.transpose(np.stack([y[43: -1], y[44: ]])))
# 绘制训练与测试数据的结果
comp = pd.DataFrame()
comp['original'] = y
# 拼接预测结果与之前的数据绘制图像
comp['predict'] = np.concatenate([y[: 44], predicts], axis=-1)
comp.plot()
plt.show()
