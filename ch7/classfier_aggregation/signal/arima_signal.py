from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox

import statsmodels as sm
import numpy as np

from vnpy_ctastrategy import (
    BarData,
    ArrayManager,
)

from . import Trend

class ARIMASignal:
    """ ARIMA交易信号 """
    author = "ouyangpengcheng"

    window_size = 50

    fixed_size = 1
    vt_symbol = None

    parameters = [
        "window_size", "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    def __init__(self):
        self.prefetch_num = self.window_size

        self.array_manager = ArrayManager(self.prefetch_num)
        self.highs = None
        self.lows = None
        self.opens = None
        self.closes = None
        self.volumes = None

    def on_bar(self, bar: BarData) -> Trend:
        """
        Callback of new bar data update.
        """
        am = self.array_manager

        am.update_bar(bar)

        if not am.inited:
            return Trend.UNKNOWN

        self.highs = am.high[-self.prefetch_num:]
        self.lows = am.low[-self.prefetch_num:]
        self.opens = am.open[-self.prefetch_num:]
        self.closes = am.close[-self.prefetch_num:]
        self.volumes = am.volume[-self.prefetch_num:]

        prices = self.closes
        prices_diff = prices

        # 平稳性检验
        dftest = adfuller(prices, autolag='AIC')
        d = 0

        while dftest[1] > 0.05:
            prices_diff = np.diff(prices_diff)
            dftest = adfuller(prices_diff, autolag='AIC')
            d += 1

        # 对差分后的数据进行白噪声检验
        noise_test = acorr_ljungbox(prices_diff)

        # 使用AIC定阶
        aic_pq = sm.tsa.stattools.arma_order_select_ic(prices_diff, max_ar=4, max_ma=4, ic='aic')['aic_min_order']
        # 使用BIC定阶
        bic_pq = sm.tsa.stattools.arma_order_select_ic(prices_diff, max_ar=4, max_ma=4, ic='bic')['bic_min_order']

        order = aic_pq
        if sum(order) > sum(bic_pq):
            order = bic_pq
        order = (order[0], d, order[-1])

        train = prices
        model = ARIMA(train, order=order).fit()
        # 计算模型对训练数据的拟合程度
        delta = model.fittedvalues - train
        score = 1 - delta.var() / train.var()
        # 向后预测一个价格
        predict = np.squeeze(model.predict(self.window_size, self.window_size, dynamic=True))

        # 如果模型对训练数据拟合效果较好并且数据不为白噪声, 则进行进一步交易
        if score > 0.8 and (noise_test['lb_pvalue'] <= 0.05).all():
            if predict > self.closes[-1]:
                return Trend.UP
            elif predict < self.closes[-1]:
                return Trend.DOWN
        else:
            return Trend.UNKNOWN

        return Trend.UNKNOWN
