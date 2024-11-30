from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)

from vnpy.trader.object import TradeData, Offset

class DualThrustStrategy(CtaTemplate):
    """ DualThrust策略 """
    author = "ouyangpengcheng"

    fixed_size = 1
    k1 = 0.4
    k2 = 0.6
    # window_size表示天数
    window_size = 20

    bars = []

    parameters = ["k1", "k2", "fixed_size", "window_size"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        # 天数转为分钟数
        self.window_size = round(4.25 * 60 * self.window_size)
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bar_generator = BarGenerator(self.on_bar)
        self.array_manager = ArrayManager(self.window_size)

        self.highs = None
        self.lows = None
        self.opens = None
        self.closes = None
        self.volumes = None

        # 每一个小时获取一次小时线的开盘价, 在分钟线进行操作
        self.open_price_this_period = None
        # 今天是否开仓
        self.today_open = False

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(self.window_size)

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
        self.array_manager.update_bar(bar)

        if not self.array_manager.inited:
            return

        if not self.trading:
            return

        bar_time = bar.datetime.strftime('%H%M%S')
        # 收盘后重置开仓标志
        if '150000' <= bar_time <= '210000':
            self.today_open = False
        # 如果是当天第一根K线, 则记录其开盘价(对于夜盘品种而言)
        if bar_time == '210000':
            self.open_price_this_period = bar.open_price

        if self.open_price_this_period is None:
            return

        self.highs = self.array_manager.high[-self.window_size:]
        self.lows = self.array_manager.low[-self.window_size:]
        self.opens = self.array_manager.open[-self.window_size:]
        self.closes = self.array_manager.close[-self.window_size:]
        self.volumes = self.array_manager.volume[-self.window_size:]


        window_hh = max(self.highs)
        window_lc = min(self.closes)
        window_hc = max(self.closes)
        window_ll = min(self.lows)

        window_range = max(window_hh - window_lc, window_hc - window_ll)
        upper_bound = self.open_price_this_period + self.k1 * window_range
        lower_bound = self.open_price_this_period - self.k2 * window_range
        
        # 价格大于上界则开多或平空
        if bar.close_price > upper_bound:
            if self.pos < 0:
                self.cover(upper_bound, abs(self.pos))
            if self.pos == 0 and not self.today_open:
                self.buy(upper_bound, self.fixed_size)
        # 价格小于下界则开空或平多
        elif bar.close_price < lower_bound:
            if self.pos > 0:
                self.sell(lower_bound, abs(self.pos))
            if self.pos == 0 and not self.today_open:
                self.short(lower_bound, self.fixed_size)
        self.put_event()

    def on_trade(self, trade: TradeData):
        """ 成交时的回调 """
        # 如果是开仓, 则记录今天已开仓
        if trade.offset == Offset.OPEN:
            self.today_open = True
