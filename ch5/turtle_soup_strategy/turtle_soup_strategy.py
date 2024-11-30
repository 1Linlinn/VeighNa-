import numpy as np

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    TradeData,
    BarGenerator,
    ArrayManager,
)
from vnpy.trader.object import Offset, Direction

class TurtleSoupStrategy(CtaTemplate):
    """ 海龟汤交易策略 """
    author = "ouyangpengcheng"

    fixed_size = 1
    window_size = 20

    parameters = ["window_size"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bar_generator = BarGenerator(self.on_bar)
        self.am = ArrayManager(self.window_size)
        self.stop_order_ids = []

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
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        price = bar.close_price

        today_low = False
        # 获取上一个窗口期内的最低价
        last_low = np.min(self.am.low[-(self.window_size + 1): -1])
        # 如果当前价格小于上一个最低价, 则当天信号成立
        if price < last_low:
            today_low = True

        # 获取上一个最低价距离今天的日数
        last_low_period = np.argmin(self.am.low[-(self.window_size + 1): -1]) < self.window_size - 4

        # 如果当天是最低价并且上一个最低价距离今日超过4天
        if today_low and last_low_period:
            # 以最低价向上上浮5个tick, 开多单
            self.buy(last_low + 5 * self.get_pricetick(), self.fixed_size, stop=True)
        # 如果持有多仓, 则判断是否需要止盈
        if self.pos > 0:
            # 使用窗口内的最高价进行止盈
            self.sell(np.max(self.am.high[-(self.window_size + 1): -1]), abs(self.pos), stop=True)
            # 当主动止盈平仓后, 需要将之前的止损单撤销
            for si in self.stop_order_ids:
                self.cancel_order(si)
            self.stop_order_ids = []

        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        if trade.offset == Offset.OPEN:
            if trade.direction == Direction.LONG:
                # 如果开多单, 则需要在最低价之下一个tick挂止损单
                stop_loss_ids = self.sell(self.am.low[-1] - self.get_pricetick(), trade.volume, stop=True)
                self.stop_order_ids.extend(stop_loss_ids)
