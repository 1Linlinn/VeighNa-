from enum import Enum
from typing import Tuple

from PyEMD import EMD
import numpy as np

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)

class Trend(Enum):
    """ 趋势的枚举类 """
    RISE = 1
    DOWN = -1
    UNSURE = 0

class EMDStrategy(CtaTemplate):
    """ 经验模态分解下的趋势交易策略 """
    author = "ouyangpengcheng"

    emd_window_size = 100
    fixed_size = 1

    vt_symbol = None

    parameters = [
        "emd_window_size",
        "fixed_size",
    ]

    variables = [
        "vt_symbol",
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol

        self.bar_generator = BarGenerator(self.on_bar)
        self.array_manager = ArrayManager(self.emd_window_size)
        self.highs = None
        self.lows = None
        self.opens = None
        self.closes = None
        self.volumes = None

        self.last_trend = Trend.UNSURE.value

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(self.emd_window_size)

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

    @staticmethod
    def get_trend(data: np.array) -> Trend:
        """ 判断数据的趋势性 """
        data_diff = np.diff(data)
        if data_diff.shape[0] == 0:
            return Trend.UNSURE
        if (data_diff > 0).all():
            return Trend.RISE
        if (data_diff < 0).all():
            return Trend.DOWN
        return Trend.UNSURE

    @staticmethod
    def get_emd(data: np.array) -> Tuple[np.array, np.array, Trend]:
        """ EMD分解 """
        emd = EMD()
        emd.emd(data)
        imfs, residual = emd.get_imfs_and_residue()
        trend = EMDStrategy.get_trend(residual)
        trend_value = trend.value
        return imfs, residual, trend_value

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.write_log(f'Received Bar Data: {bar}')

        self.cancel_all()

        array_manager = self.array_manager
        array_manager.update_bar(bar)

        if not array_manager.inited:
            return

        array_manager = self.array_manager

        self.highs = array_manager.high[-self.emd_window_size:]
        self.lows = array_manager.low[-self.emd_window_size:]
        self.opens = array_manager.open[-self.emd_window_size:]
        self.closes = array_manager.close[-self.emd_window_size:]
        self.volumes = array_manager.volume[-self.emd_window_size:]

        _, _, trend_value = self.get_emd(self.closes)

        if self.last_trend > 0 and trend_value <= 0:
            # 如果上一次的emd值大于0(表示之前在涨), 当前emd值小于等于0(表示当下可能会跌)
            price = bar.close_price
            open_size = self.fixed_size
            if self.pos > 0:
                # 由涨转跌的行情如果持有多仓, 则需要平多
                price = bar.close_price
                self.sell(price, abs(self.pos))
            if self.pos == 0:
                self.short(price, open_size)
        elif self.last_trend < 0 and trend_value >= 0:
            # 如果上一次的emd值小于0(表示之前在跌), 当前emd值大于等于0(表示当下可能会涨)
            price = bar.close_price
            open_size = self.fixed_size
            if self.pos < 0:
                # 由跌转涨的行情如果持有空仓, 则需要平空
                price = bar.close_price
                self.cover(price, abs(self.pos))
            if self.pos == 0:
                self.buy(price, open_size)

        self.last_trend = trend_value
        self.put_event()
