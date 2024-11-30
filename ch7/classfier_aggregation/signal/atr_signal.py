import talib

from vnpy_ctastrategy import (
    BarData,
    ArrayManager,
)

from . import Trend

class AtrSignal:
    """ ATR交易信号 """
    author = "ouyangpengcheng"

    atr_period = 60
    buy_factor = 2
    sell_factor = 2

    fixed_size = 1

    vt_symbol = None

    parameters = [
        "atr_period", "buy_factor", "sell_factor", "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    def __init__(self):
        self.prefetch_num = 2 * self.atr_period

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

        atr_index = talib.ATR(self.highs, self.lows, self.closes, timeperiod=self.atr_period)

        # 当期价格触及前期收盘价+平均波动作为超买线
        sell_line = self.closes[-2] + atr_index[-1] * self.sell_factor
        # 当期价格触及前期收盘价-平均波动作为超卖线
        buy_line = self.closes[-2] - atr_index[-1] * self.buy_factor

        # 当期价格收至超卖线以下则开多仓
        if self.closes[-1] < buy_line:
            return Trend.UP
        # 当期价格收至超买线以上则开空仓
        elif self.closes[-1] > sell_line:
            return Trend.DOWN

        # 当期价格收至超买线以上则平多仓
        if self.closes[-1] > sell_line:
            return Trend.DOWN

        # 当期价格收至超卖线以下则平空仓
        if self.closes[-1] < buy_line:
            return Trend.UP

        return Trend.UNKNOWN
