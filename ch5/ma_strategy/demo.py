test_list = [1, 3, 2, 5, 4, 9, 8, 7]
period = 3

ma_list = []
for i in range(len(test_list) + 1):
    if i >= period:
        # 计算下标i及其前period个元素的均值
        ma = sum(test_list[i - period: i]) / period
        ma_list.append(ma)

print(ma_list)

import talib
import numpy as np

print(
    talib.SMA(
        np.asarray(test_list).astype(np.float64),
        timeperiod=period
    )
)
