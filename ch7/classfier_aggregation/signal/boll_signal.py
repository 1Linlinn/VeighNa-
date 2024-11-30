import talib

from vnpy_ctastrategy import (
    BarData,
    ArrayManager,
)

from . import Trend

class BollSignal:
    """ 布林带交易信号 """
    author = "ouyangpengcheng"

    boll_period = 8
    nbdev_up = 1.9
    nbdev_down = 1.9
    ma_type = 0

    fixed_size = 1

    vt_symbol = None

    parameters = [
        "boll_period", "nbdev_up", "nbdev_down", "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    def __init__(self):
        self.prefetch_num = 2 * self.boll_period

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

        upper, middle, lower = talib.BBANDS(self.closes,
                                            timeperiod=self.boll_period,
                                            nbdevup=self.nbdev_up,
                                            nbdevdn=self.nbdev_down,
                                            matype=self.ma_type)

        # 上轨走势向上
        upper_up = upper[-1] > upper[-2] > upper[-3]
        # 中轨走势向上
        middle_up = middle[-1] > middle[-2] > middle[-3]
        # 下轨走势向上
        lower_up = lower[-1] > lower[-2] > lower[-3]

        # 上轨走势向下
        upper_down = upper[-1] < upper[-2] < upper[-3]
        # 中轨走势向下
        middle_down = middle[-1] < middle[-2] < middle[-3]
        # 下轨走势向下
        lower_down = lower[-1] < lower[-2] < lower[-3]

        # 如果三条轨道同时向上并价格高于中轨, 则开多仓
        if upper_up and middle_up and lower_up and bar.close_price > middle[-1]:
            return Trend.UP
        # 如果三条轨道同时向下并价格低于中轨, 则开空仓
        elif upper_down and middle_down and lower_down and bar.close_price < middle[-1]:
            return Trend.DOWN

        # 如果价格大于上轨或小于中轨, 则平多仓
        if bar.close_price > upper[-1] or bar.close_price < middle[-1]:
            return Trend.DOWN

        # 如果价格小于下轨或大于中轨, 则平空仓
        if bar.close_price < lower[-1] or bar.close_price > middle[-1]:
            return Trend.UP

        return Trend.UNKNOWN
