import talib

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)

class BollStrategy(CtaTemplate):
    """ 布林带交易策略 """
    author = "ouyangpengcheng"

    boll_period = 22
    nbdev_up = 2.0
    nbdev_down = 2.0
    ma_type = 0

    fixed_size = 1

    vt_symbol = None

    parameters = [
        "boll_period", "nbdev_up", "nbdev_down", "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol

        self.prefetch_num = 2 * self.boll_period

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

        upper, middle, lower = talib.BBANDS(self.closes,
                                            timeperiod=self.boll_period,
                                            nbdevup=self.nbdev_up,
                                            nbdevdn=self.nbdev_down,
                                            matype=self.ma_type)

        # 上轨走势向上
        upper_up = upper[-1] > upper[-2] > upper[-3]
        # 中轨走势向上
        middle_up = middle[-1] > middle[-2] > middle[-3]
        # 下轨走势向上
        lower_up = lower[-1] > lower[-2] > lower[-3]

        # 上轨走势向下
        upper_down = upper[-1] < upper[-2] < upper[-3]
        # 中轨走势向下
        middle_down = middle[-1] < middle[-2] < middle[-3]
        # 下轨走势向下
        lower_down = lower[-1] < lower[-2] < lower[-3]

        if self.pos == 0:
            size = self.fixed_size
            # 如果三条轨道同时向上并价格高于中轨, 则开多仓
            if upper_up and middle_up and lower_up and bar.close_price > middle[-1]:
                price = bar.close_price
                self.buy(price, size)
            # 如果三条轨道同时向下并价格低于中轨, 则开空仓
            elif upper_down and middle_down and lower_down and bar.close_price < middle[-1]:
                price = bar.close_price
                self.short(price, size)
        elif self.pos > 0:
            # 如果价格大于上轨或小于中轨, 则平多仓
            if bar.close_price > upper[-1] or bar.close_price < middle[-1]:
                price = bar.close_price
                size = abs(self.pos)
                self.sell(price, size)
        elif self.pos < 0:
            # 如果价格小于下轨或大于中轨, 则平空仓
            if bar.close_price < lower[-1] or bar.close_price > middle[-1]:
                price = bar.close_price
                size = abs(self.pos)
                self.cover(price, size)

        self.put_event()
