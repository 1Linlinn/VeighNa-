import pandas as pd
pd.set_option('display.max_rows', None)

# 读取csv数据
data = pd.read_csv('fu888.csv')
# print(data)
# 获取开盘/最高/最低/收盘价
opens = data.loc[:, 'open']
highs = data.loc[:, 'high']
lows = data.loc[:, 'low']
closes = data.loc[:, 'close']
# ==============================================
import talib
# 计算周期为5天的收盘价的移动平均值
sma = talib.SMA(closes, timeperiod=5)
# print(sma)
# ==============================================
# 使用定义计算MACD
ema_fast = talib.EMA(closes, timeperiod=3)
ema_slow = talib.EMA(closes, timeperiod=5)
dif = ema_fast - ema_slow
dea = talib.EMA(dif, timeperiod=2)
macd_hist = (dif - dea)
# print(macd_hist)

# 直接使用talib计算MACD
macd, macd_signal, macd_hist = talib.MACD(closes, fastperiod=3, slowperiod=5, signalperiod=2)
# print(macd_hist)
# ==============================================
res = talib.CDLDARKCLOUDCOVER(opens, highs, lows, closes, penetration=0.5)
print(res)