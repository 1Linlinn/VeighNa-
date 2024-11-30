import argparse

def parse_str():
    # 创建parser
    parser = argparse.ArgumentParser()
    # 为parser添加一个名为vvv（简称v）的参数，其默认值为string
    parser.add_argument('-v', '--vvv', default='string')
    # 解析参数
    args = parser.parse_args()
    return args

args = parse_str()
# 打印Namespace
print(args)
# 打印接受的参数及其类型
print(args.vvv, type(args.vvv))

# ================================================
def parse_int():
    # 创建parser
    parser = argparse.ArgumentParser()
    # 为parser添加一个名为iii（简称i）的参数，其默认值为0，限制传入的类型为整型
    parser.add_argument('-i', '--iii', default=0, type=int)
    # 解析参数
    args = parser.parse_args()
    return args

# args = parse_int()
# # 打印Namespace
# print(args)
# # 打印接受的参数及其类型
# print(args.iii, type(args.iii))
# ================================================
# b = True
# if b == True:
#     pass
# if b:
#     pass
# ================================================
def parse_bool():
    # 创建parser
    parser = argparse.ArgumentParser()
    # 为parser添加一个名为bbb（简称b）的参数，其默认值为False，若命令写出--bbb（-b）则值为True
    parser.add_argument('-b', '--bbb', default=False, action='store_true')
    # 为parser添加一个名为ppp（简称p）的参数，其默认值为True，若命令写出--ppp（-p）则值为False
    parser.add_argument('-p', '--ppp', default=True, action='store_false')
    # 解析参数
    args = parser.parse_args()
    return args

# args = parse_bool()
# # 打印Namespace
# print(args)
# # 打印接受的参数及其类型
# print(args.bbb, type(args.bbb), args.ppp, type(args.ppp))
# ================================================
def parse_list():
    # 创建parser
    parser = argparse.ArgumentParser()
    # 为parser添加一个名为eee（简称e）的参数，若命令多次使用--eee（-e），则将结果以列表的extend形式连接
    parser.add_argument('-e', '--eee', action='append')
    # 为parser添加一个名为lll（简称l）的参数，将传入的参数返回为一个list
    parser.add_argument('-l', '--lll', nargs='+', type=int)
    # 解析参数
    args = parser.parse_args()
    return args

# args = parse_list()
# # 打印Namespace
# print(args)
# # 打印接受的参数及其类型
# print(args.eee, type(args.eee), args.lll, type(args.lll))