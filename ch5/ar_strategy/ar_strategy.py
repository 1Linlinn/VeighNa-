from typing import List

import numpy as np
from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)

class ArStrategy(CtaTemplate):
    """ Ar交易策略 """
    author = "ouyangpengcheng"

    ar_period = 26
    ar_upper = 120
    ar_overbuy = 150
    ar_lower = 80
    ar_oversell = 70

    fixed_size = 1

    vt_symbol = None

    parameters = [
        "ar_period", "ar_upper", "ar_overbuy", "ar_lower", "ar_oversell",
        "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol
        self.prefetch_num = self.ar_period

        self.bar_generator = BarGenerator(self.on_bar)
        self.array_manager = ArrayManager(self.prefetch_num)
        self.highs = None
        self.lows = None
        self.opens = None
        self.closes = None
        self.volumes = None
        self.ar_arr: List[float] = []

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

    def calc_ar_index(self):
        """ 计算ar指标值 """
        _highs = np.asarray(self.highs[-self.prefetch_num:])
        _opens = np.asarray(self.opens[-self.prefetch_num:])
        _lows = np.asarray(self.lows[-self.prefetch_num:])

        return np.sum(_highs - _opens) / (np.sum(_opens - _lows) + 1e-6) * 100

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

        ar_index = self.calc_ar_index()
        self.ar_arr.append(ar_index)

        # 需要积累至少两个ar值进行趋势的判断
        if len(self.ar_arr) < 2:
            return

        if self.pos == 0:
            size = self.fixed_size
            # 如果人气值上升并且小于70并且无持仓, 则做多
            if self.ar_arr[-2] < self.ar_arr[-1] and ar_index < self.ar_oversell:
                price = bar.close_price
                self.buy(price, size)
            # 如果人气值下降并且大于150并且无持仓, 则做空
            elif self.ar_arr[-2] > self.ar_arr[-1] and ar_index > self.ar_overbuy:
                price = bar.close_price
                self.short(price, size)
        elif self.pos > 0:
            # 如果人气值上升并且进入盘整行情, 则平多
            if self.ar_arr[-2] < self.ar_arr[-1] and self.ar_lower < ar_index < self.ar_upper:
                price = bar.close_price
                size = abs(self.pos)
                self.sell(price, size)

        elif self.pos < 0:
            # 如果人气值下降并且进入盘整行情, 则平空
            if self.ar_arr[-2] > self.ar_arr[-1] and self.ar_lower < ar_index < self.ar_upper:
                price = bar.close_price
                size = abs(self.pos)
                self.cover(price, size)

        self.put_event()
