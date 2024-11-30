from vnpy.trader.optimize import OptimizationSetting
from vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy_ctastrategy.strategies.atr_rsi_strategy import (
    AtrRsiStrategy,
)
from datetime import datetime

engine = BacktestingEngine()

# 设置回测参数, 与界面左侧的配置框对应
engine.set_parameters(
    vt_symbol="IF888.CFFEX",
    interval="1m",
    start=datetime(2019, 1, 1),
    end=datetime(2019, 4, 30),
    rate=0.3/10000,
    slippage=0.2,
    size=300,
    pricetick=0.2,
    capital=1_000_000,
)
# 添加待回测策略
engine.add_strategy(AtrRsiStrategy, {})

# 加载数据
engine.load_data()
# 执行回测
engine.run_backtesting()
# 计算回测结果, 对应界面的中间部分表格
df = engine.calculate_result()
engine.calculate_statistics()
# 展示图形, 对应界面的右侧绘制区
engine.show_chart()

# 优化参数
setting = OptimizationSetting()
# 定义优化目标
setting.set_target("sharpe_ratio")
# 定义待优化参数及其范围与步长
setting.add_parameter("atr_length", 25, 27, 1)
setting.add_parameter("atr_ma_length", 10, 30, 10)

# 使用遗传算法完成参数优化
engine.run_ga_optimization(setting)
# 使用暴力求解完成参数优化
engine.run_bf_optimization(setting)
