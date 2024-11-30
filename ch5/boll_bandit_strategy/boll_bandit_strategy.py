import talib

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)

class BollBanditStrategy(CtaTemplate):
    """ 布尔海盗交易策略 """
    author = "ouyangpengcheng"

    boll_period = 50
    nbdev_up = 1.0
    nbdev_down = 1.0
    init_ma_period = 50
    min_ma_period = 10
    ma_type = 0

    fixed_size = 1

    vt_symbol = None

    parameters = [
        "boll_period", "nbdev_up", "nbdev_down", "init_ma_period", "min_ma_period", "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol

        self.prefetch_num = 2 * max(self.boll_period, self.init_ma_period, self.min_ma_period)
        self.ma_period = self.init_ma_period

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

        upper, _, lower = talib.BBANDS(self.closes,
                                       timeperiod=self.boll_period,
                                       nbdevup=self.nbdev_up,
                                       nbdevdn=self.nbdev_down,
                                       matype=self.ma_type)
        ma = talib.SMA(self.closes, self.ma_period)

        if self.pos == 0:
            size = self.fixed_size

            if self.closes[-1] < lower[-1]:
                price = bar.close_price
                self.buy(price, size)
            elif self.closes[-1] > upper[-1]:
                price = bar.close_price
                self.short(price, size)
            self.ma_period = self.init_ma_period

        elif self.pos > 0:
            if self.closes[-1] > lower[-1] or self.closes[-1] > ma[-1]:
                price = bar.close_price
                size = abs(self.pos)
                self.sell(price, size)
            self.ma_period = max(self.ma_period - 1, self.min_ma_period)

        elif self.pos < 0:
            if self.closes[-1] < upper[-1] or self.closes[-1] < ma[-1]:
                price = bar.close_price
                size = abs(self.pos)
                self.cover(price, size)
            self.ma_period = max(self.ma_period - 1, self.min_ma_period)

        self.put_event()
