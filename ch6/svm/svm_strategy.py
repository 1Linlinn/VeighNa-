from sklearn.svm import SVR
import numpy as np

from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    BarGenerator,
    ArrayManager,
)

class SVMStrategy(CtaTemplate):
    """ SVM交易策略 """
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

        # 构造训练数据与标签
        train_y = np.transpose(np.stack([prices[: -2], prices[1: -1]]))
        label_y = prices[2: ]

        svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
        # 模型拟合训练数据
        svr_rbf.fit(train_y, label_y)

        # 向后预测一个价格
        predict = np.squeeze(svr_rbf.predict(np.reshape([prices[-1], prices[-2]], newshape=(1, 2))))

        # 预测价格上涨
        if predict > self.closes[-1]:
            # 无持仓则开仓
            if self.pos == 0:
                price = bar.close_price
                self.buy(price, self.fixed_size)
            # 有空仓则反手
            elif self.pos < 0:
                price = bar.close_price
                size = abs(self.pos)
                self.cover(price, size)
                self.buy(price, self.fixed_size)
        # 预测价格会下跌
        elif predict < self.closes[-1]:
            # 无持仓则开空
            if self.pos == 0:
                price = bar.close_price
                self.short(price, self.fixed_size)
            # 有多仓则反手
            elif self.pos > 0:
                price = bar.close_price
                size = abs(self.pos)
                self.sell(price, size)
                self.short(price, self.fixed_size)
        self.put_event()
