import numpy as np
import talib

from vnpy_ctastrategy import (
    BarData,
    ArrayManager,
)

from . import Trend

def bias(price, period: int):
    """ 计算乖离率 """
    price = np.asarray(price)
    ma = talib.SMA(price, timeperiod=period)
    last_price = price[-1]
    return (last_price - ma[-1]) / ma[-1] * 100

class BiasSignal:
    """ BIAS交易信号 """
    author = "ouyangpengcheng"

    bias_term1 = 4
    bias_term2 = 10
    bias_term3 = 24

    fixed_size = 1

    vt_symbol = None

    parameters = [
        "bias_term1",
        "bias_term2",
        "bias_term3",
        "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    def __init__(self):
        self.prefetch_num = 2 * max(self.bias_term1, self.bias_term2, self.bias_term3)

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

        bias1 = bias(self.closes, self.bias_term1)
        bias2 = bias(self.closes, self.bias_term3)
        bias3 = bias(self.closes, self.bias_term3)

        # 三个bias值同时发出信号
        if bias1 < -5 and bias2 < -7 and bias3 < -11:
            return Trend.UP
        elif bias1 > 5 and bias2 > 7 and bias3 > 11:
            return Trend.DOWN

        return Trend.UNKNOWN
