import talib

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)


class MacdStrategy(CtaTemplate):
    """ MACD交易策略 """
    author = "ouyangpengcheng"

    long_term = 26
    short_term = 12
    macd_term = 9

    fixed_size = 1

    vt_symbol = None

    parameters = [
        "long_term",
        "short_term",
        "macd_term",
        "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol

        self.prefetch_num = 2 * max(self.long_term, self.short_term, self.macd_term)

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

        dif, dea, macd = talib.MACD(
                            self.closes,
                            fastperiod=self.short_term,
                            slowperiod=self.long_term,
                            signalperiod=self.macd_term
                        )

        # 满足以下条件则进行多头的开仓或反手: DIF上穿DEA线形成金叉
        if (dif[-1] > 0 and dea[-1] > 0 and \
           dif[-1] > dif[-2] > dif[-3] and dif[-2] < dea[-2] and dif[-1] > dea[-1]):
            if self.pos < 0:
                price = bar.close_price
                size = abs(self.pos)
                if size > 0:
                    self.cover(price, size)
                self.buy(price, self.fixed_size)
        # 满足以下条件则进行空头开仓或反手: DIF下穿DEA线形成死叉
        elif (dif[-1] < 0 and dea[-1] < 0 and \
             dif[-1] < dif[-2] < dif[-3] and dif[-2] > dea[-2] and dif[-1] < dea[-1]):
            if self.pos >= 0:
                price = bar.close_price
                size = abs(self.pos)
                if size > 0:
                    self.sell(price, size)
                self.short(price, self.fixed_size)

        self.put_event()
