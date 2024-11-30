import numpy as np
import talib

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)

def bias(price, period: int):
    """ 计算乖离率 """
    price = np.asarray(price)
    ma = talib.SMA(price, timeperiod=period)
    last_price = price[-1]
    return (last_price - ma[-1]) / ma[-1] * 100

class BiasStrategy(CtaTemplate):
    """ BIAS交易策略 """
    author = "ouyangpengcheng"

    bias_term1 = 6
    bias_term2 = 12
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

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol

        self.prefetch_num = 2 * max(self.bias_term1, self.bias_term2, self.bias_term3)

        self.bar_generator = BarGenerator(self.on_bar)
        self.array_manager = ArrayManager(self.prefetch_num)
        self.highs = None
        self.lows = None
        self.opens = None
        self.closes = None
        self.volumes = None

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(self.prefetch_num)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bar_generator.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.cancel_all()
        am = self.array_manager

        am.update_bar(bar)
        self.write_log(f'Received Bar Data: {bar}')

        if not am.inited:
            return

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
            if self.pos < 0:
                price = bar.close_price
                size = abs(self.pos)
                if size > 0:
                    self.cover(price, size)
                self.buy(price, self.fixed_size)
        elif bias1 > 5 and bias2 > 7 and bias3 > 11:
            if self.pos >= 0:
                price = bar.close_price
                size = abs(self.pos)
                if size > 0:
                    self.sell(price, size)
                self.short(price, self.fixed_size)

        self.put_event()
