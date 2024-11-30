import numpy as np
import scipy.io as io

# 初始化3个数据
# 模拟一张16*16的3通道图像
ones_matrix = np.ones([16, 16, 3])
# 模拟一张32*32的单通道图像
zeros_matrix = np.zeros([32, 32])
# 模拟一张256*256的单通道图像
random_matrix = np.random.randn(256, 256)

# 以字典的形式整理数据
data = {
    'ones_matrix': ones_matrix,
    'zeros_matrix': zeros_matrix,
    'random_matrix': random_matrix
}

mat_filename = 'data.mat'

# 将数据存入data.mat
io.savemat(mat_filename, data)

# ================================================
# 载入mat文件
load_data = io.loadmat(mat_filename)
# 查看mat文件中有哪些变量
print(load_data.keys())
# 查看mat文件中字段的内容及其形状
print(load_data['ones_matrix'])
print(load_data['ones_matrix'].shape)
print(load_data['zeros_matrix'])
print(load_data['zeros_matrix'].shape)
print(load_data['random_matrix'].shape)
