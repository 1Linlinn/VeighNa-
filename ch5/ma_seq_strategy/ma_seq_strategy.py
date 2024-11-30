from typing import List
import numpy as np
import talib

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)


class MaSeqStrategy(CtaTemplate):
    """ 均线排列交易策略 """
    author = "ouyangpengcheng"
    MIN_PERIOD = 1

    window_size = 90
    fixed_size = 1

    vt_symbol = None

    last_signal = 0

    parameters = [
        "window_size", "fixed_size"
    ]

    variables = [
        "vt_symbol", "last_trend"
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

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(self.window_size)

    @staticmethod
    def calculate_ma_price(price: np.array, period: int) -> np.array:
        """ 计算指定周期的平均价格 """
        return talib.MA(price, timeperiod=period)

    def calculate_ma_sequence(self, price: np.array, max_period: int) -> List[float]:
        """ 计算不同周期均线值 """
        ma_seq = []
        for i in range(max_period, 0, -1):
            ma_seq.append(self.calculate_ma_price(price, i)[-1])
        return ma_seq

    def calculate_signal(self, price: np.array, max_period: int) -> float:
        """ 根据不同周期均线值计算信号 """
        ma_seq = self.calculate_ma_sequence(price, max_period)
        # 计算周期减小的均线值之差
        ma_seq_diff = np.diff(ma_seq)
        # 如果均线值之差大于0, 则记为1; 均线值之差小于0, 则记为-1, 否则记为0
        ma_seq_diff_norm = [x / abs(x) if x != 0 else 0 for x in ma_seq_diff]
        # 所有归一化后的均线值之差求和作为走势信号
        return sum(ma_seq_diff_norm)

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

        signal = self.calculate_signal(self.closes, max_period=self.window_size)

        if self.pos == 0:
            size = self.fixed_size
            # 现在信号为涨势, 则开多
            if signal > 0:
                price = bar.close_price
                self.buy(price, size)
            # 现在信号为跌势, 则开空
            elif signal < 0:
                price = bar.close_price
                self.short(price, size)
        if self.pos > 0:
            # 上次信号为涨势, 现在信号为跌, 则平多
            if self.last_signal > 0 and signal <= 0:
                long_stop = bar.close_price
                size = abs(self.pos)
                self.sell(long_stop, size)
        elif self.pos < 0:
            # 上次信号为跌势, 现在信号为涨, 则平空
            if self.last_signal < 0 and signal >= 0:
                short_stop = bar.close_price
                size = abs(self.pos)
                self.cover(short_stop, size)

        self.last_signal = signal

        self.put_event()
