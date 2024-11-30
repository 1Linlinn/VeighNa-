import talib

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)

class AtrStrategy(CtaTemplate):
    """ ATR交易策略 """
    author = "ouyangpengcheng"

    atr_period = 26
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

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol

        self.prefetch_num = 2 * self.atr_period

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

        atr_index = talib.ATR(self.highs, self.lows, self.closes, timeperiod=self.atr_period)

        # 当期价格触及前期收盘价+平均波动作为超买线
        sell_line = self.closes[-2] + atr_index[-1] * self.sell_factor
        # 当期价格触及前期收盘价-平均波动作为超卖线
        buy_line = self.closes[-2] - atr_index[-1] * self.buy_factor

        if self.pos == 0:
            size = self.fixed_size
            # 当期价格收至超卖线以下则开多仓
            if self.closes[-1] < buy_line:
                price = bar.close_price
                self.buy(price, size)
            # 当期价格收至超买线以上则开空仓
            elif self.closes[-1] > sell_line:
                price = bar.close_price
                self.short(price, size)
        elif self.pos > 0:
            # 当期价格收至超买线以上则平多仓
            if self.closes[-1] > sell_line:
                price = bar.close_price
                size = abs(self.pos)
                self.sell(price, size)
        elif self.pos < 0:
            # 当期价格收至超卖线以下则平空仓
            if self.closes[-1] < buy_line:
                price = bar.close_price
                size = abs(self.pos)
                self.cover(price, size)

        self.put_event()
