import talib

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)

class AdxStrategy(CtaTemplate):
    """ Adx交易策略 """
    author = "ouyangpengcheng"

    adx_period = 6
    di_period = 14

    fixed_size = 1

    vt_symbol = None

    parameters = [
        "adx_period", "di_period", "fixed_size"
    ]

    variables = [
        "vt_symbol",
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol

        self.prefetch_num = 3 * max(self.adx_period, self.di_period)

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

        adx = talib.ADX(self.highs, self.lows, self.closes, timeperiod=self.adx_period)
        plus_di = talib.PLUS_DI(self.highs, self.lows, self.closes, timeperiod=self.di_period)
        minus_di = talib.MINUS_DI(self.highs, self.lows, self.closes, timeperiod=self.di_period)

        # adx值增加说明趋势增加并且已经大于50
        if adx[-2] < adx[-1] and adx[-1] > 50:
            size = self.fixed_size

            # +DI线上穿-DI线
            plus_di_up_cross_minus_di = plus_di[-1] > minus_di[-1] and plus_di[-2] < minus_di[-2]

            # +DI线下穿-DI线
            plus_di_down_cross_minus_di = plus_di[-2] > minus_di[-2] and plus_di[-1] < minus_di[-1]

            if plus_di_up_cross_minus_di:
                price = bar.close_price
                if self.pos < 0:
                    self.cover(price, abs(self.pos))
                self.buy(price, size)

            # +DI线下穿-DI线
            elif plus_di_down_cross_minus_di:
                price = bar.close_price
                if self.pos > 0:
                    self.sell(price, abs(self.pos))
                self.short(price, size)
        # adx值减小并且已经低于20
        elif adx[-2] > adx[-1] and adx[-1] < 20:
            price = bar.close_price
            if self.pos > 0:
                self.sell(price, abs(self.pos))
            elif self.pos < 0:
                self.cover(price, abs(self.pos))

        self.put_event()
