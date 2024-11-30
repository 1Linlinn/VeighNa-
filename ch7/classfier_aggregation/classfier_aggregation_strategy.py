from typing import List
from pathlib import Path

import numpy as np
import os

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
)

from .signal import Trend

from .signal.adx_signal import AdxSignal
from .signal.ar_signal import ArSignal
# from .signal.arima_signal import ARIMASignal
# from .signal.arma_signal import ARMASignal
from .signal.atr_signal import AtrSignal
from .signal.bias_signal import BiasSignal
# from .signal.boll_bandit_signal import BollBanditSignal
from .signal.boll_signal import BollSignal
from .signal.cmo_signal import CmoSignal
from .signal.emd_signal import EMDSignal
from .signal.kdj_signal import KdjSignal
from .signal.ma_seq_signal import MaSeqSignal
from .signal.ma_signal import MaSignal
from .signal.macd_signal import MacdSignal
# from .signal.sarima_signal import SARIMASignal
# from .signal.super_trend_signal import SuperTrendSignal
# from .signal.svm_signal import SVMSignal
# from .signal.visual_ae_strategy import VisualAeSignal

class ClassfierAggregationStrategy(CtaTemplate):
    """ 基于分类器集成的交易策略 """
    author = "ouyangpengcheng"

    window_size = 50
    fixed_size = 1
    vt_symbol = None

    parameters = [
        "window_size", "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    signals = [
        AdxSignal(),
        ArSignal(),
        AtrSignal(),
        BiasSignal(),
        # BollBanditSignal(),
        BollSignal(),
        CmoSignal(),
        EMDSignal(),
        KdjSignal(),
        MaSeqSignal(),
        MaSignal(),
        MacdSignal(),
        # SuperTrendSignal(),
        # 以下子策略无法在区间内获得正收益
        # ARIMASignal(),
        # ARMASignal(),
        # SARIMASignal(),
        # SVMSignal(),
        # VisualAeSignal()
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol
        self.prefetch_num = self.window_size
        self.bar_generator = BarGenerator(self.on_bar)
        self.signal_decisions = []

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
        numpy_decisions = np.array(self.signal_decisions)
        # 保存不同子策略的信号结果
        np.save(os.path.join(Path(__file__).parent, 'decisions.npy'), numpy_decisions)
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bar_generator.update_tick(tick)

    def all_signals_inited(self):
        """ 检测是否所有交易信号都初始化 """
        inited = True
        for signal in self.signals:
            inited = inited and signal.array_manager.inited
        return inited

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.cancel_all()
        self.write_log(f'Received Bar Data: {bar}')

        deal_signal: List[Trend] = []

        for signal in self.signals:
            deal_signal.append(signal.on_bar(bar))

        if not self.all_signals_inited():
            return

        deal_signal_value = [x.value for x in deal_signal]
        # 记录不同信号的信号发生结果
        self.signal_decisions.append(deal_signal_value)

        # 计算软投票值
        squeezed_signal = sum(deal_signal_value) / len(deal_signal)
        if squeezed_signal > 0.01:
            if self.pos < 0:
                self.cover(bar.close_price, abs(self.pos))
                self.buy(bar.close_price, self.fixed_size)
            if self.pos == 0:
                self.buy(bar.close_price, self.fixed_size)
        elif squeezed_signal < -0.01:
            if self.pos > 0:
                self.sell(bar.close_price, abs(self.pos))
                self.short(bar.close_price, self.fixed_size)
            if self.pos == 0:
                self.short(bar.close_price, self.fixed_size)
        else:
            if self.pos > 0:
                self.sell(bar.close_price, abs(self.pos))
            if self.pos < 0:
                self.cover(bar.close_price, abs(self.pos))

        self.put_event()
