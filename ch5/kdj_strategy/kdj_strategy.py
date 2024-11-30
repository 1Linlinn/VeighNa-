import talib

from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
from vnpy.trader.constant import Interval

class KdjStrategy(CtaTemplate):
    """ Kdj交易策略 """
    author = "ouyangpengcheng"

    fastk_period = 9
    slowk_period = 3
    slowk_matype = 0
    slowd_period = 3
    slowd_matype = 0

    slowk_bid = 20
    slowk_sell = 80
    slowd_bid = 20
    slowd_sell = 80
    j_bid = 0
    j_sell = 100

    fixed_size = 1

    vt_symbol = None
    intra_trade_high = 0
    intra_trade_low = 0

    win_times = 1
    lose_times = 1

    win_profit = 0
    lose_profit = 0

    amount_ratio = 0

    parameters = [
        "fastk_period",
        "slowk_period",
        "slowd_period",
        "slowk_bid",
        "slowk_sell",
        "slowd_bid",
        "slowd_sell",
        "j_bid",
        "j_sell",
        "fixed_size",
    ]

    variables = [
        "vt_symbol", "intra_trade_high", "intra_trade_low"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol
        self.prefetch_num = 2 * max(self.fastk_period, self.slowk_period, self.slowd_period)

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

        slowk, slowd = talib.STOCH(high=self.highs,
                                   low=self.lows,
                                   close=self.closes,
                                   fastk_period=self.fastk_period,
                                   slowk_period=self.slowk_period,
                                   slowk_matype=self.slowk_matype,
                                   slowd_period=self.slowd_period,
                                   slowd_matype=self.slowd_matype)
        j = 3 * slowk[-1] - 2 * slowd[-1]

        size = self.fixed_size

        # K/D/J值发出买入信号或发生金叉
        rise_signal = j < self.j_bid or \
                      (slowk[-1] > slowk[-2] > slowk[-3] and \
                        slowk[-1] > slowd[-1] and \
                            slowk[-2] < slowd[-2])

        # K/D/J值发出卖出信号或发生死叉
        down_signal = j > self.j_sell or \
                      (slowk[-1] < slowk[-2] < slowk[-3] and \
                        slowk[-1] < slowd[-1] and \
                            slowk[-2] > slowd[-2])


        if rise_signal:
            # 反手或开多
            if self.pos <= 0:
                price = bar.close_price
                size = abs(self.pos)
                if size > 0:
                    self.cover(price, size)
                self.buy(price, self.fixed_size)
        elif down_signal:
            # 反手或开空
            if self.pos >= 0:
                price = bar.close_price
                size = abs(self.pos)
                if size > 0:
                    self.sell(price, size)
                self.short(price, self.fixed_size)
        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
