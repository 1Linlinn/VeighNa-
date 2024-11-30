a: str = 2
# 期望接受一个类型为str的参数, 没有返回值
def print_var(v: str) -> None:
    print(v)
# =======================================
# 整型变量
int_var: int = 1
# 浮点型变量
float_var: float = 1.0
# 布尔型变量
bool_var: bool = True
# 复数型变量
complex_var: complex = 1 + 2j
# 字符串变量
str_var: str = '1'
# 相加一个整型变量和一个浮点型变量并返回
def func_with_type(i: int, f: float, b: bool, c: complex, s: str) -> float:
    return i + f
# ========================================
from typing import List
# 标识元素为整型值的列表
list_var: List[int] = [1, 2, 3, 4]
# ========================================
from typing import Tuple, Set, Dict
# 含有4个不同类型元素的元组
tuple_var: Tuple[int, str, float, bool] = [1, '2', '3.0', False]
# 元素为整型变量的集合
set_var: Set[int] = {1, 2, 3, 4}
# 键为字符串值为整型值的字典
dict_var: Dict[str, int] = {'1': 1, '2': 2, '3': 3}
# ========================================
# 标识元素为整型值的列表
list_var2: list[int] = [1, 2, 3, 4]
# 含有4个不同类型元素的元组
tuple_var2: tuple[int, str, float, bool] = [1, '2', '3.0', False]
# 元素为整型变量的集合
set_var2: set[int] = {1, 2, 3, 4}
# 键为字符串值为整型值的字典
dict_var2: dict[str, int] = {'1': 1, '2': 2, '3': 3}
# ========================================
combined_var: tuple[list[int], tuple[int, str, float, bool], dict[str, int]] = None
# ========================================
# 自定义类型别名
A = list[int]
B = tuple[int, str, float, bool]
C = dict[str, int]
combined_var2: tuple[A, B, C] = ([1, ], (1, '2', 3., True), {'1': 1})
# ========================================
from typing import Union
int_str_var: list[Union[int, str]] = ['a', 2, 'b', 4]
# Python 3.10及以后
int_str_var2: list[int | str] = ['a', 2, 'b', 4]
# ========================================
from typing import NamedTuple
# 相当于collections.namedtuple('Address', ['ip', 'port])
class Address(NamedTuple):
    ip: str
    port: int
address = Address(ip='127.0.0.1', port=80)
# ========================================
from typing import Counter as TCnt, OrderedDict as TOrdD, DefaultDict as TDD
from collections import Counter, OrderedDict, defaultdict

# Counter的value必定为int, 因此只需要标识key的类型
counter: TCnt[str] = Counter('aabbccddefg')
od: TOrdD[str, str] = OrderedDict()
dd: TDD[str, str] = defaultdict(str)
# Python 3.9之后
counter2: Counter[str] = Counter('aabbccddefg')
od2: OrderedDict[str, str] = OrderedDict()
dd2: defaultdict[str, str] = defaultdict()
# ========================================
from typing import Callable
# 传入的函数参数接收一个整型值作为参数并且返回值为str
def wrapper1(func: Callable[[int], str]):
    return func(0)
# 传入的函数参数介绍任意的可变参数, 无返回值
def wrapper2(func: Callable[..., None]):
    func()
# ========================================
from typing import NoReturn
# 包含死循环的函数
def func_while() -> NoReturn:
    from time import sleep
    while True:
        sleep(1)
# 必定会抛出异常的函数
def func_exc(num: int) -> NoReturn:
    raise ValueError(f'Bad Value: {num}')
# ========================================
from typing import Optional
# 期望传入一个类型为整型或浮点型的参数, 允许传入None
def func_with_optional_param(num: Optional[Union[int, float]]):
    if num is None:
        raise ValueError(f'Unexpected value: {num}')
    print(num)
# ========================================
from typing import Literal
MODE = Literal['r', 'rb', 'w', 'wb']
# 打开文件
def open_helper(file: str, mode: MODE) -> str:
    with open(file, mode, encoding='utf8'):
        pass
    return ''
