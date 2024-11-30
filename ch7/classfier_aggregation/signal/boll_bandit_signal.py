import talib

from vnpy_ctastrategy import (
    BarData,
    ArrayManager,
)

from . import Trend

class BollBanditSignal:
    """ 布尔海盗交易信号 """
    author = "ouyangpengcheng"

    boll_period = 50
    nbdev_up = 1.0
    nbdev_down = 1.0
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

        upper, _, lower = talib.BBANDS(self.closes,
                                       timeperiod=self.boll_period,
                                       nbdevup=self.nbdev_up,
                                       nbdevdn=self.nbdev_down,
                                       matype=self.ma_type)
        if self.closes[-1] < lower[-1]:
            return Trend.UP
        elif self.closes[-1] > upper[-1]:
            return Trend.DOWN

        if self.closes[-1] > lower[-1]:
            return Trend.DOWN

        if self.closes[-1] < upper[-1]:
            return Trend.UP

        return Trend.UNKNOWN
