import talib

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)

class CmoStrategy(CtaTemplate):
    """ CMO交易策略 """
    author = "ouyangpengcheng"

    cmo_period = 30

    fixed_size = 1
    vt_symbol = None

    parameters = [
        "cmo_period", "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol
        self.prefetch_num = 2 * self.cmo_period

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

        # 计算CMO指标值
        cmo = talib.CMO(self.closes, self.cmo_period)

        if self.pos == 0:
            size = self.fixed_size
            # 如果CMO值上穿0轴则开多
            if cmo[-2] < 0 and cmo[-1] > 0:
                price = bar.close_price
                self.buy(price, size)
            # 如果CMO值下穿0轴则开空
            elif cmo[-2] > 0 and cmo[-1] < 0:
                price = bar.close_price
                self.short(price, size)
        elif self.pos > 0:
            # 如果持有多仓并且CMO值大于50则说明超买, 需要平多
            if cmo[-1] > 50:
                price = bar.close_price
                size = abs(self.pos)
                self.sell(price, size)
        elif self.pos < 0:
            # 如果持有空仓并且CMO值小于-50则说明超卖, 需要平空
            if cmo[-1] < -50:
                price = bar.close_price
                size = abs(self.pos)
                self.cover(price, size)
        self.put_event()
