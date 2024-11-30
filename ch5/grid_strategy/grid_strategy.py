import math

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    TradeData,
    BarData,
    BarGenerator,
    ArrayManager,
)

from vnpy.trader.object import Direction, Offset

class GridStrategy(CtaTemplate):
    """ 网格交易策略 """
    author = "ouyangpengcheng"

    grid_interval = 50

    window_size = 2
    fixed_size = 1

    vt_symbol = None

    parameters = [
        "grid_interval",
        "fixed_size",
    ]

    variables = [
        "vt_symbol",
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol

        self.bar_generator = BarGenerator(self.on_bar)
        self.array_manager = ArrayManager(self.window_size)
        self.highs = None
        self.lows = None
        self.opens = None
        self.closes = None
        self.volumes = None

        self.base_price = None
        self.step_price = self.grid_interval

        self.pos_inited = False

    def on_init(self):
        """
        Callback when strategy is inited.
        """
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
        self.write_log(f'Received Bar Data: {bar}')
        array_manager = self.array_manager
        array_manager.update_bar(bar)

        if not array_manager.inited:
            return

        if self.base_price is None:
            self.base_price = bar.close_price
    
        price = bar.close_price
        buy_direction_steps = math.floor((self.base_price - price) / self.step_price)
        last_buy_direction_steps = math.floor((self.base_price - self.array_manager.close[-2]) / self.step_price)
        # 价格下跌(向下跨越网格边界)时买
        if buy_direction_steps > last_buy_direction_steps:
            size = self.fixed_size
            self.buy(price, size)
        self.put_event()

    def on_trade(self, trade: TradeData):
        if trade.direction == Direction.LONG:
            if trade.offset == Offset.OPEN:
                # 当开多单时, 挂出对应的止盈单(向上一个网格宽度)
                self.sell(trade.price + self.step_price, trade.volume, stop=True)
