import numpy as np

def f(x):
    """ 生成随机序列的函数 """
    return np.sin(x) + np.random.rand(*x.shape) - 0.5

import matplotlib.pyplot as plt

np.random.seed(1234)
x = np.linspace(-10, 10, 50)
y = f(x)
plt.plot(x, y)
plt.show()

from statsmodels.tsa.stattools import adfuller

dftest = adfuller(y, autolag='AIC')
print(dftest)
if dftest[1] > 0.05:
    print("序列不平稳")
else:
    print("序列平稳")

from statsmodels.stats.diagnostic import acorr_ljungbox
noise_test = acorr_ljungbox(y)
print(noise_test)
if (noise_test['lb_pvalue'] > 0.05).any():
    print('序列为白噪声')
else:
    print('序列为非白噪声')

from statsmodels.tsa.stattools import acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# 计算自相关系数
lag_acf = acf(y, nlags=20)
# 计算偏自相关系数
lag_pacf = pacf(y, nlags=20, method='ols')

fig, axes = plt.subplots(1,2, figsize=(20,5))
plot_acf(y, lags=20, ax=axes[0])
plot_pacf(y, lags=20, ax=axes[1])
plt.show()

import statsmodels as sm

# 使用AIC定阶
aic_pq = sm.tsa.stattools.arma_order_select_ic(y, max_ar=6, max_ma=6, ic='aic')['aic_min_order']
# 使用BIC定阶
bic_pq = sm.tsa.stattools.arma_order_select_ic(y, max_ar=6, max_ma=6, ic='bic')['bic_min_order']
print(aic_pq, bic_pq)

from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

# p, d, q值分别为2, 0, 2
order = (2, 0, 2)
# 使用除了最后5个数据进行训练
train = y[: -5]
# 使用最后5个数进行验证
test = y[-5: ]
# ARIMA中d值为0则退化为ARMA模型
model = ARIMA(train, order=order).fit()
# 计算模型对训练数据的拟合程度
delta = model.fittedvalues - train
score = 1 - delta.var() / train.var()
print(score)
# 使用训练好的模型对后5个数进行预测
predicts = model.predict(6, 10, dynamic=True)
# 绘制训练与测试数据的结果
comp = pd.DataFrame()
comp['original'] = y
comp['predict'] = np.concatenate([train, predicts], axis=-1)
comp.plot()
plt.show()
