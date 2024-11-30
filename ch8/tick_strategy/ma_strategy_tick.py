from typing import List
import numpy as np

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
)

import talib

class MaStrategyTick(CtaTemplate):
    """ 均线策略 """
    author = "ouyangpengcheng"

    fast_window = 5
    slow_window = 10
    fixed_size = 1

    fast_ma0 = 0.0
    fast_ma1 = 0.0

    slow_ma0 = 0.0
    slow_ma1 = 0.0

    parameters = ["fast_window", "slow_window", "fixed_size"]
    variables = ["fast_ma0", "fast_ma1", "slow_ma0", "slow_ma1"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.tick_data: List[TickData] = []

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")

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
        self.tick_data.append(tick)
        tick_data_num = len(self.tick_data)

        if tick_data_num > self.fast_window and tick_data_num > self.slow_window:
            prices = list((t.ask_price_1 + t.bid_price_1) / 2 for t in self.tick_data)

            # ArrayManager中的sma方法底层直接调用talib.SMA
            # 计算5日均线
            np_prices = np.asarray(prices)
            fast_ma = talib.SMA(np_prices, self.fast_window)
            # 判断交叉至少需要两个点
            # 因此获取最近一天和最近第二天的5日均线值
            self.fast_ma0 = fast_ma[-1]
            self.fast_ma1 = fast_ma[-2]

            # 计算10日均线
            slow_ma = talib.SMA(prices, self.slow_window)
            # 获取最近一天和最近第二天的10日均线值
            self.slow_ma0 = slow_ma[-1]
            self.slow_ma1 = slow_ma[-2]

            # 如果最近一天5日均线值大于10日均线值
            # 并且最近第二天的5日均线值小于10日均线值
            # 则说明最近一天5日均线完成了对10日均线的上穿(金叉)
            cross_over = self.fast_ma0 > self.slow_ma0 and self.fast_ma1 < self.slow_ma1

            # 如果最近一天5日均线值小于10日均线值
            # 并且最近第二天的5日均线值大于10日均线值
            # 则说明最近一天5日均线完成了对10日均线的下穿(死叉)
            cross_below = self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1

            # 如果发生了金叉
            if cross_over:
                if self.pos == 0:
                    # 无持仓则开多仓
                    self.buy(prices[-1], self.fixed_size)
                elif self.pos < 0:
                    # 如果持有空仓则先平仓再开多仓
                    self.cover(prices[-1], abs(self.pos))
                    self.buy(prices[-1], self.fixed_size)
            # 如果发生了死叉
            elif cross_below:
                if self.pos == 0:
                    # 无持仓则开空仓
                    self.short(prices[-1], self.fixed_size)
                elif self.pos > 0:
                    # 如果持仓多仓则先平仓再开空仓
                    self.sell(prices[-1], abs(self.pos))
                    self.short(prices[-1], self.fixed_size)

            self.put_event()
