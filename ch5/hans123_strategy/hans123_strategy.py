import numpy as np

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)

class Hans123Strategy(CtaTemplate):
    """ Hans123交易策略 """
    author = "ouyangpengcheng"

    hans_period = 30

    fixed_size = 1

    vt_symbol = None

    parameters = [
        "hans_period", "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol

        self.prefetch_num = self.hans_period

        self.bar_generator = BarGenerator(self.on_bar)
        self.array_manager = ArrayManager(self.prefetch_num)
        self.highs = None
        self.lows = None
        self.opens = None
        self.closes = None
        self.volumes = None

        self.upper = None
        self.lower = None

        # 该交易时间段是否开仓
        self.today_open = False
        # 该交易时间段收到的bar数
        self.cnt = 0

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

        self.highs = am.high[-self.prefetch_num:]
        self.lows = am.low[-self.prefetch_num:]
        self.opens = am.open[-self.prefetch_num:]
        self.closes = am.close[-self.prefetch_num:]
        self.volumes = am.volume[-self.prefetch_num:]

        bar_time = bar.datetime.strftime('%H%M%S')
        price = bar.close_price

        # 收盘后重置当天开仓标志位和当前交易时段已记录的bar数
        # 上午9点是一个连续交易时段的开始, 进行相同操作
        if '150000' <= bar_time <= '210000' or bar_time == '090000':
            self.today_open = False
            self.cnt = 0

        # 在每个连续交易时段的前prefetch_num分钟不交易, 观察最高价与最低价
        if self.cnt < self.prefetch_num:
            self.cnt += 1
            # 获取窗口内的最小值与最大值
            self.upper = np.max(self.highs)
            self.lower = np.min(self.lows)
            return

        self.write_log(f'Received Bar Data: {bar}')

        # 连续交易时段结束前5分钟, 开始平仓
        if '145500' <= bar_time <= '145900' or '225500' <= bar_time <= '225900':
            if self.pos > 0:
                self.sell(price, abs(self.pos))
            elif self.pos < 0:
                self.cover(price, abs(self.pos))
            return

        if not am.inited:
            return

        size = self.fixed_size

        # 如果今天没有开仓, 则根据信号开仓
        if not self.today_open:
            if self.pos == 0:
                # if bar.close_price > self.upper:
                if bar.close_price > self.upper * 1.01:
                    price = bar.close_price
                    self.buy(price, size)
                    self.today_open = True
                # elif bar.close_price < self.lower:
                elif bar.close_price < self.lower * 0.99:
                    price = bar.close_price
                    self.short(price, size)
                    self.today_open = True
        else:
            # 如果今天开过仓, 则根据信号平仓
            # if bar.close_price > self.upper:
            if bar.close_price > self.lower:
                if self.pos < 0:
                    price = bar.close_price
                    self.cover(price, abs(self.pos))
            # elif bar.close_price < self.lower:
            elif bar.close_price < self.upper:
                if self.pos > 0:
                    price = bar.close_price
                    self.sell(price, abs(self.pos))

        self.put_event()
