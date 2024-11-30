import talib

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)


class SuperTrendStrategy(CtaTemplate):
    """ 超级趋势交易策略 """
    author = "ouyangpengcheng"

    atr_period = 20
    atr_shifting_coff = 2.0

    fixed_size = 1

    vt_symbol = None


    parameters = [
        "atr_period", "atr_shifting_coff", "fixed_size"
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

        self.upper_last = -1e100
        self.lower_last = 1e100

        self.last_trend = 0

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
        array_manager = self.array_manager

        array_manager.update_bar(bar)
        self.write_log(f'Received Bar Data: {bar}')

        if not array_manager.inited:
            return

        self.highs = array_manager.high
        self.lows = array_manager.low
        self.opens = array_manager.open
        self.closes = array_manager.close
        self.volumes = array_manager.volume

        middle = (self.highs[-1] + self.lows[-1]) / 2

        atr_index = talib.ATR(self.highs, self.lows, self.closes, timeperiod=self.atr_period)
        upper = middle + self.atr_shifting_coff * atr_index[-1]
        lower = middle - self.atr_shifting_coff * atr_index[-1]
        
        # 收盘价高于上次的上轨, 则尝试获取更高的上轨
        if bar.close_price > self.upper_last:
            upper = max(upper, self.upper_last)
        # 收盘价低于上次的下轨, 则尝试获取更低的下轨
        if bar.close_price < self.lower_last:
            lower = min(lower, self.lower_last)

        # 收盘价比下轨高, 则认为后市可能上涨
        if bar.close_price > lower:
            trend = 1
        # 收盘价比上轨低, 则认为后市可能下跌
        elif bar.close_price < upper:
            trend = -1
        else:
            trend = 0

        # 趋势从下跌转为上涨, 开多或反手
        if self.last_trend == -1 and trend == 1:
            if self.pos < 0:
                price = bar.close_price
                size = abs(self.pos)
                self.cover(price, size)
            if self.pos == 0:
                size = self.fixed_size
                price = bar.close_price
                self.buy(price, size)
        # 趋势由上涨转为下跌, 开空或反手
        elif self.last_trend == 1 and trend == -1:
            if self.pos > 0:
                price = bar.close_price
                size = abs(self.pos)
                self.sell(price, size)
            if self.pos == 0:
                size = self.fixed_size
                price = bar.close_price
                self.short(price, size)
        # 更新历史量
        self.upper_last = upper
        self.lower_last = lower
        self.last_trend = trend

        self.put_event()
