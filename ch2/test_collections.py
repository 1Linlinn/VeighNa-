from collections import namedtuple

# 创建一个表示四通道图像的namedtuple
Channel = namedtuple('ImageChannels', field_names=['R', 'G', 'B', 'A'])
ch = Channel(R=127, G=200, B=255, A=100)
# 获取四通道中的R通道值
print(ch[0], ch.R)
# ====================================
from collections import Counter
# 待计数的字符串
s = 'abbcdd'
# 直接传入字符串进行计数
counter1 = Counter(s)
# 传入列表进行计数
counter2 = Counter(list(s))
# 传入元组进行计数
counter3 = Counter(tuple(s))
# 传入字典进行计数
counter4 = Counter({'a': 1, 'b': 2, 'c': 1, 'd': 2})
print(counter1, counter2, counter3, counter4)
# =====================================
from collections import OrderedDict
# 创建OrderedDict对象
od = OrderedDict()
# 向OrderedDict中存放值
od['A'] = 'a'
od['B'] = 'b'
od['C'] = 'c'
# 读取OrderedDict中的值
for k, v in od.items():
    print(k, v)
# =====================================
# 创建只包含一个元素的字典
d = {'ip': '127.0.0.1'}
# 尝试访问一个字典中不存在的元素会抛出KeyError
# port = d['port']
# 在使用之前判断字典中是否有键
port = d['port'] if 'port' in d else None
# 使用get方法赋予默认值
port = d.get('port')

from collections import defaultdict
# 创建一个默认值为80的defaultdict
dd = defaultdict(lambda: 80)
dd['ip'] = '127.0.0.1'
# 返回80
port = dd['port']
