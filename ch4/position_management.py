from dataclasses import dataclass

# 当前仓位
pos = 0
available = 100000

@dataclass
class Trade:
    """ 交易的数据类 """
    # 交易的标的
    symbol: str
    # 交易的方向
    direction: str
    # 交易的价格
    price: float
    # 交易的数量
    size: int

def buy(symbol, price, size):
    """ 买入的函数 """
    global pos, available
    pos += size
    available -= size * price

def sell(symbol, price, size):
    """ 卖出的函数 """
    global pos, available
    pos -= size
    available += size * price

def fixed_position(trade: Trade, max_pos=None, fixed_size=1, mode='quantity'):
    """ 固定仓位管理策略 """
    if max_pos is not None and pos >= max_pos:
        return

    if mode == 'quantity':
        size = fixed_size
    else:
        size = int(fixed_size * available / trade.price)

    if trade.direction == 'buy':
        buy(trade.symbol, trade.price, size)
    elif trade.direction == 'sell':
        sell(trade.symbol, trade.price, size)

# 漏斗形仓位管理策略的初始下单比例
funnel_ratio = 0.1
# 记录上一次的价格,用于判断市场状态
last_price = None

def funnel_position(trade: Trade, ratio_step=0.1):
    """ 漏斗形仓位管理策略 """
    global funnel_ratio, last_price

    if last_price is not None:
        # 市场未发生下行
        if last_price < trade.price:
            return

    size = int(funnel_ratio * available / trade.price)

    if trade.direction == 'buy':
        buy(trade.symbol, trade.price, size)
    
    last_price = trade.price
    funnel_ratio += ratio_step
    funnel_ratio = min(funnel_ratio, 1)

# 金字塔形初始下单比例
pyramid_ratio = 0.5

def pyramid_position(trade: Trade, ratio_step=0.1):
    """ 金字塔形仓位管理策略 """
    global pyramid_ratio, last_price
    
    if last_price is not None:
        # 市场未发生上行
        if last_price > trade.price:
            return

    size = int(pyramid_ratio * available / trade.price)

    if trade.direction == 'buy':
        buy(trade.symbol, trade.price, size)
    
    last_price = trade.price
    pyramid_ratio -= ratio_step
    pyramid_ratio = max(pyramid_ratio, 0)


# 马丁策略上一次下单量
last_size = 1

def martin_position(trade: Trade):
    """ 马丁策略 """
    global last_size

    if <出现了亏损>:
        last_size *= 2
        buy(trade.symbol, trade.price, last_size)

# 反马丁策略上一次下单量
last_size = 1

def anti_martin_position(trade: Trade):
    """ 反马丁策略 """
    global last_size

    if <产生了盈利>:
        last_size *= 2
        buy(trade.symbol, trade.price, last_size)
