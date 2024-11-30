from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
)

class RBreakStrategy(CtaTemplate):
    """ R-Breaker交易策略 """
    author = "ouyangpengcheng"

    fixed_size = 1

    # 突破买入价
    buy_break = 0
    # 观察卖出价
    sell_setup = 0
    # 反转卖出价
    sell_enter = 0
    # 反转买入价
    buy_enter = 0
    # 观察买入价
    buy_setup = 0
    # 突破卖出价
    sell_break = 0

    parameters = ["fixed_size"]
    variables = ["buy_break", "sell_setup", "sell_enter", "buy_enter", "buy_setup", "sell_break"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.new_day = False
        self.bar_generator = BarGenerator(self.on_bar)

        self.day_high = 0
        self.day_open = 0
        self.day_close = 0
        self.day_low = 0

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

        bar_time = bar.datetime.strftime('%H%M%S')

        # 行情数据左对齐, 因此可以使用bar数据的时间判断是否是新的一天开始的行情
        self.new_day = '150000' <= bar_time <= '210000'
        price = bar.close_price

        # 收盘前5分钟, 开始平仓
        if '145500' <= bar_time <= '145900':
            if self.pos > 0:
                self.sell(price, abs(self.pos))
            elif self.pos < 0:
                self.cover(price, abs(self.pos))
            return

        # 如果是新的一天的行情, 则使用记录的昨天OHLC数据进行计算
        if self.new_day:
            if self.day_open:
                pivot = (self.day_high + self.day_low + self.day_close) / 3
                self.buy_setup = pivot - (self.day_high - self.day_low)
                self.sell_setup = pivot + (self.day_high - self.day_low)

                self.buy_enter = 2 * pivot - self.day_high
                self.sell_enter = 2 * pivot - self.day_low

                self.buy_break = self.day_high + 2 * (pivot - self.day_low)
                self.sell_break = self.day_low - 2 * (self.day_high - pivot)

            self.day_open = bar.open_price
            self.day_high = bar.high_price
            self.day_close = bar.close_price
            self.day_low = bar.low_price
        else:
            # 如果不是新的一天的行情, 则更新当天行情的价格
            self.day_high = max(self.day_high, bar.high_price)
            self.day_low = min(self.day_low, bar.low_price)
            self.day_close = bar.close_price

        # 趋势策略
        if self.pos == 0:
            if price > self.buy_break:
                self.buy(price, self.fixed_size)
            elif price < self.sell_break:
                self.short(price, self.fixed_size)
        elif self.pos > 0:
            if price <= self.buy_break:
                self.sell(price, abs(self.pos))
        elif self.pos < 0:
            if price >= self.sell_break:
                self.cover(price, abs(self.pos))

        # # 反转策略
        # # 如果当天的最高价高于观察卖出价
        # if self.day_high > self.sell_setup:
        #     # 当前价格小于反转卖出价, 说明价格从上下跌到反转卖出价
        #     # 进行开空或者反手
        #     if price < self.sell_enter:
        #         if self.pos > 0:
        #             self.sell(price, abs(self.pos))
        #         if self.pos == 0:
        #             self.short(price, self.fixed_size)
        # # 如果当天的最低价小于观察买入价
        # if self.day_low < self.buy_setup:
        #     # 当前价格大于反转买入价, 说明价格从下上涨到反转买入价
        #     # 进行开多或者反手
        #     if price > self.buy_enter:
        #         if self.pos < 0:
        #             self.cover(price, abs(self.pos))
        #         if self.pos == 0:
        #             self.buy(price, self.fixed_size)
