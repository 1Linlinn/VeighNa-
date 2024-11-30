import talib
import numpy as np

def bias(price, period: int):
    """ 计算乖离率 """
    price = np.asarray(price)
    ma = talib.SMA(price, timeperiod=period)
    last_price = price[-1]
    return (last_price - ma[-1]) / ma[-1] * 100
