from typing import List

import numpy as np
from vnpy_ctastrategy import (
    BarData,
    ArrayManager,
)

from . import Trend

class ArSignal:
    """ Ar交易信号 """
    author = "ouyangpengcheng"

    ar_period = 16
    ar_upper = 110
    ar_overbuy = 150
    ar_lower = 100
    ar_oversell = 90

    fixed_size = 1

    vt_symbol = None

    parameters = [
        "ar_period", "ar_upper", "ar_overbuy", "ar_lower", "ar_oversell",
        "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    def __init__(self):
        self.prefetch_num = self.ar_period

        self.array_manager = ArrayManager(self.prefetch_num)
        self.highs = None
        self.lows = None
        self.opens = None
        self.closes = None
        self.volumes = None
        self.ar_arr: List[float] = []

    def calc_ar_index(self):
        """ 计算ar指标值 """
        _highs = np.asarray(self.highs[-self.prefetch_num:])
        _opens = np.asarray(self.opens[-self.prefetch_num:])
        _lows = np.asarray(self.lows[-self.prefetch_num:])

        return np.sum(_highs - _opens) / (np.sum(_opens - _lows) + 1e-6) * 100

    def on_bar(self, bar: BarData) -> Trend:
        """
        Callback of new bar data update.
        """
        am = self.array_manager

        am.update_bar(bar)

        if not am.inited:
            return Trend.UNKNOWN

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

        # 如果人气值上升并且小于70并且无持仓, 则做多
        if self.ar_arr[-2] < self.ar_arr[-1] and ar_index < self.ar_oversell:
            return Trend.UP
        # 如果人气值下降并且大于150并且无持仓, 则做空
        elif self.ar_arr[-2] > self.ar_arr[-1] and ar_index > self.ar_overbuy:
            return Trend.DOWN

        # 如果人气值上升并且进入盘整行情, 则平多
        if self.ar_arr[-2] < self.ar_arr[-1] and self.ar_lower < ar_index < self.ar_upper:
            return Trend.DOWN

        # 如果人气值下降并且进入盘整行情, 则平空
        if self.ar_arr[-2] > self.ar_arr[-1] and self.ar_lower < ar_index < self.ar_upper:
            return Trend.UP

        return Trend.UNKNOWN
