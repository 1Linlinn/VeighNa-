from statsmodels.tsa.statespace.sarimax import SARIMAX

import numpy as np

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)

class SARIMAStrategy(CtaTemplate):
    """ SARIMA交易策略 """
    author = "ouyangpengcheng"

    window_size = 200

    fixed_size = 1
    vt_symbol = None

    parameters = [
        "window_size", "fixed_size"
    ]

    variables = [
        "vt_symbol"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.vt_symbol = vt_symbol
        self.prefetch_num = self.window_size

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

        prices = self.closes
        prices_diff = prices

        order = (14, 0, 16)
        s = 22
        seasonal_order = (1, 1, 1, s)
        train = prices
        model = SARIMAX(train, order=order, seasonal_order=seasonal_order).fit()
        # 计算模型对训练数据的拟合程度, 前周期个值预测差值很大, 不计入方差计算
        delta = model.fittedvalues[s: ] - train[s: ]
        score = 1 - delta.var() / train.var()
        # 向后预测一个价格
        predict = np.squeeze(model.predict(self.window_size, self.window_size, dynamic=True))

        # 如果模型对训练数据拟合效果较好, 则进行进一步交易
        if score > 0.8:
            if predict > self.closes[-1]:
                if self.pos == 0:
                    price = bar.close_price
                    self.buy(price, self.fixed_size)
                elif self.pos < 0:
                    price = bar.close_price
                    size = abs(self.pos)
                    self.cover(price, size)
            elif predict < self.closes[-1]:
                if self.pos == 0:
                    price = bar.close_price
                    self.short(price, self.fixed_size)
                elif self.pos > 0:
                    price = bar.close_price
                    size = abs(self.pos)
                    self.sell(price, size)
        else:
            if self.pos > 0:
                price = bar.close_price
                size = abs(self.pos)
                self.sell(price, size)
            elif self.pos < 0:
                price = bar.close_price
                size = abs(self.pos)
                self.cover(price, size)
        self.put_event()
