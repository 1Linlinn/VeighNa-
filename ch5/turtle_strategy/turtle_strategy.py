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

class TurtleStrategy(CtaTemplate):
    """ 海龟交易策略 """
    author = "ouyangpengcheng"

    capital = 100_000
    commission = 0.00025

    entry_window = 20
    exit_window = 10
    atr_window = 20

    entry_up = 0
    entry_down = 0
    exit_up = 0
    exit_down = 0
    atr_value = 0

    parameters = ["entry_window", "exit_window", "atr_window"]
    variables = ["entry_up", "entry_down", "exit_up", "exit_down", "atr_value"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.window_size = 2 * max(self.entry_window, self.exit_window, self.atr_window)
        self.bar_generator = BarGenerator(self.on_bar)
        self.am = ArrayManager(self.window_size)
        self.unit = 0
        self.open_price = None
        self.short_price = None
        self.size = self.get_size()

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

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        # 唐奇安通道的信号产生为今日价格与前一天的通道值进行比较
        # 无持仓时, 计算开仓使用的唐奇安通道
        if not self.pos:
            self.entry_up = np.max(self.am.high_array[-(self.entry_window + 1): -1])
            self.entry_down = np.min(self.am.low_array[-(self.entry_window + 1): -1])

        # 动态计算退场时的唐奇安通道值
        self.exit_up = np.max(self.am.high_array[-(self.exit_window + 1): -1])
        self.exit_down = np.min(self.am.low_array[-(self.exit_window + 1): -1])
        # 计算ATR
        self.atr_value = self.am.atr(self.atr_window)

        price = bar.close_price
        if not self.pos:
            # 根据目前的现金权益计算下单单位
            self.unit = int(0.01 * self.capital / (self.atr_value * self.size))
            if self.unit > 0:
                # 价格大于开仓唐奇安通道上轨则开多一个单位
                if price > self.entry_up:
                    self.open_price = price
                    self.buy(price, self.unit)
                # 价格低于开仓唐奇安通道下轨则开空一个单位
                elif price < self.entry_down:
                    self.short_price = price
                    self.short(price, self.unit)
        elif self.pos > 0:
            # 价格高于开仓价格的0.5到2倍atr考虑加多(趋势正在延续)
            open_low = self.open_price + self.atr_value * 0.5
            open_high = self.open_price + self.atr_value * 2
            if open_low < price < open_high:
                # 控制手中仓位不会太大, 最多持仓4手, 防止大回撤造成的亏损
                if self.pos < 4:
                    # 加仓单位的数量与初始仓位的开仓价和atr值相关, 为0.5atr的n倍
                    unit_num = int((price - self.open_price) / (self.atr_value * 0.5))
                    self.buy(price,  unit_num * self.unit)
            # 价格低于开仓价格减2倍atr则止损
            elif price < self.open_price - self.atr_value * 2:
                self.sell(price, abs(self.pos))
            # 唐奇安通道止盈条件
            elif price < self.exit_down:
                self.sell(price, abs(self.pos))
        elif self.pos < 0:
            # 价格低于开仓价格的2倍到0.5倍atr考虑加空(趋势正在延续)
            open_low = self.short_price - self.atr_value * 2
            open_high = self.short_price - self.atr_value * 0.5
            if open_low < price < open_high:
                # 控制手中仓位不会太大, 最多持仓4手, 防止大回撤造成的亏损
                if self.pos > -4:
                    # 加仓单位的数量与初始仓位的开仓价和atr值相关, 为0.5atr的n倍
                    unit_num = int((self.short_price - price) / (self.atr_value * 0.5))
                    self.short(price,  unit_num * self.unit)
            # 价格高于开仓价格加2倍atr则止损
            elif price > self.short_price + self.atr_value * 2:
                self.cover(price, abs(self.pos))
            # 唐奇安通道止盈条件
            elif price > self.exit_up:
                self.cover(price, abs(self.pos))

        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        size = self.size
        direction = trade.direction
        offset = trade.offset

        # 合约交易金额=价格*数量*合约乘数
        # 未考虑保证金的影响
        turnover = trade.price * trade.volume * size
        # 计算佣金(commission为佣金费率)
        commission = turnover * self.commission

        # 去除佣金
        self.capital -= commission

        # 为简化计算, 直接将持仓合约的金额从现金权益中扣除, 不计算持仓权益
        # 与真实资金计算不同
        if offset == Offset.OPEN:
            if direction == Direction.LONG:
                # 多开则减去合约交易金额
                self.capital -= turnover
            elif direction == Direction.SHORT:
                # 空开则加上合约交易金额
                self.capital += turnover
        elif offset == Offset.CLOSE:
            if direction == Direction.SHORT:
                # 平多仓则加合约交易金额
                self.capital += turnover
            elif direction == Direction.LONG:
                # 平空仓则减合约交易金额
                self.capital -= turnover
