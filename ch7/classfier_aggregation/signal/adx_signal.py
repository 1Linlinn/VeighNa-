import talib

from vnpy_ctastrategy import (
    BarData,
    ArrayManager,
)

from . import Trend

class AdxSignal:
    """ Adx交易信号 """
    author = "ouyangpengcheng"

    adx_period = 3
    di_period = 16

    fixed_size = 1

    vt_symbol = None

    parameters = [
        "adx_period", "di_period", "fixed_size"
    ]

    variables = [
        "vt_symbol",
    ]

    def __init__(self):
        self.prefetch_num = 3 * max(self.adx_period, self.di_period)

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

        adx = talib.ADX(self.highs, self.lows, self.closes, timeperiod=self.adx_period)
        plus_di = talib.PLUS_DI(self.highs, self.lows, self.closes, timeperiod=self.di_period)
        minus_di = talib.MINUS_DI(self.highs, self.lows, self.closes, timeperiod=self.di_period)

        # adx值增加说明趋势增加并且已经大于50
        if adx[-2] < adx[-1] and adx[-1] > 50:
            # +DI线上穿-DI线
            plus_di_up_cross_minus_di = plus_di[-1] > minus_di[-1] and plus_di[-2] < minus_di[-2]

            # +DI线下穿-DI线
            plus_di_down_cross_minus_di = plus_di[-2] > minus_di[-2] and plus_di[-1] < minus_di[-1]

            if plus_di_up_cross_minus_di:
                return Trend.UP
            # +DI线下穿-DI线
            elif plus_di_down_cross_minus_di:
                return Trend.DOWN
        # adx值减小并且已经低于20
        elif adx[-2] > adx[-1] and adx[-1] < 20:
            return Trend.UNKNOWN

        return Trend.UNKNOWN
