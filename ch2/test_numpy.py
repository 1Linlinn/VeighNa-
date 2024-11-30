import numpy as np

# 方法1：通过list创建array
a_list = [
    [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]],
    [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]
]

a_np1 = np.array(a_list)
print(a_np1)
# <class 'numpy.ndarray'>
print(type(a_np1))
# <class 'numpy.int32'>
print(type(a_np1[0][0][0]))

# 方法2：通过numpy函数创建array
a_np2 = np.ones(shape=[2, 3, 4])
print(a_np2)
# <class 'numpy.ndarray'>
print(type(a_np2))
# <class 'numpy.float64'>
print(type(a_np2[0][0][0]))

# ==========================================================
a_np2_int = a_np2.astype(np.int32)
# <class 'numpy.int32'>
print(type(a_np2_int[0][0][0]))

# ==========================================================
b_np = np.zeros([2, 3, 4])
print(b_np)

# ==========================================================
# 创建和b_np数组形状相同的，其中值全为1的数组
one_like_b_np = np.ones_like(b_np)
print(one_like_b_np)
# (2, 3, 4)
print(one_like_b_np.shape)

# ==========================================================
# empty1和empty2中的值都是随机初始化的，empty方法实质上是创建了占位符，运行效率高
empty1 = np.empty([2, 3])
print(empty1)
empty2 = np.empty([2, 3, 4])
print(empty2)

# ==========================================================
# 3
print(a_np1.ndim)
# (2, 3, 4)
print(a_np1.shape)
# 24
print(a_np1.size)

# ==========================================================
b_list = [
    [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
    [[13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24]]
]

b_np = np.array(b_list)
print(b_np)
# (2, 3, 4)
print(b_np.shape)

b_np_t1 = np.transpose(b_np, axes=[0, 2, 1])
print(b_np_t1)
# (2, 4, 3)
print(b_np_t1.shape)

b_np_t2 = np.transpose(b_np, axes=[1, 0, 2])
print(b_np_t2)
# (3, 2, 4)
print(b_np_t2.shape)

b_np_t3 = np.transpose(b_np, axes=[1, 2, 0])
print(b_np_t3)
# (3, 4, 2)
print(b_np_t3.shape)

b_np_t4 = np.transpose(b_np, axes=[2, 0, 1])
print(b_np_t4)
# (4, 2, 3)
print(b_np_t4.shape)

b_np_t5 = np.transpose(b_np, axes=[2, 1, 0])
print(b_np_t5)
# (4, 3, 2)
print(b_np_t5.shape)

# ==========================================================
b_np_transpose = np.transpose(b_np, axes=[0, 2, 1])
print(b_np_transpose)
# (2, 4, 3)
print(b_np_transpose.shape)

b_np_reshape = np.reshape(b_np, newshape=[2, 4, 3])
print(b_np_reshape)
# (2, 4, 3)
print(b_np_reshape.shape)
# ==========================================================
to_split_arr = np.arange(12).reshape(3, 4)

'''
[[ 0  1  2  3]
 [ 4  5  6  7]
 [ 8  9 10 11]]
'''
print(to_split_arr)
# 形状为(3, 4)
print(to_split_arr.shape)

# [array([[0, 1, 2, 3]]), array([[4, 5, 6, 7]]), array([[ 8,  9, 10, 11]])]
axis_0_split_3_equal_parts = np.split(to_split_arr, 3)
print(axis_0_split_3_equal_parts)

'''
[array([[0, 1],
       [4, 5],
       [8, 9]]), 
 array([[2, 3],
       [6, 7],
       [10, 11]])]
'''
axis_1_split_2_equal_parts = np.split(to_split_arr, 2, axis=1)
print(axis_1_split_2_equal_parts)

# ValueError，因为轴0长度为3，无法被均分为2份
# axis_0_split_2_equal_parts = np.split(to_split_arr, 2)

'''
[array([[0, 1, 2, 3],
        [4, 5, 6, 7]]), 
 array([[8, 9, 10, 11]])]
'''
axis_0_split_indices = np.split(to_split_arr, [2, ])
print(axis_0_split_indices)

'''
[array([[ 0,  1,  2],
        [ 4,  5,  6],
        [ 8,  9, 10]]), 
 array([[ 3],
        [ 7],
        [11]])]
'''
axis_1_split_indices = np.split(to_split_arr, [3, ], axis=1)
# ==========================================================
# 新建两个形状为(3, 4)的待合并数组
merge_arr1 = np.arange(12).reshape(3, 4)
merge_arr2 = np.arange(12, 24). reshape(3, 4)

print(merge_arr1)
print(merge_arr2)

# stack为新数组新建一个轴2
stack_arr1 = np.stack([merge_arr1, merge_arr2], axis=2)
print(stack_arr1)
# (3, 4, 2)
print(stack_arr1.shape)

# stack为新数组新建一个轴1，原始的轴1变为轴2
stack_arr2 = np.stack([merge_arr1, merge_arr2], axis=1)
print(stack_arr2)
# (3, 2, 4)
print(stack_arr2.shape)

# 新数组在原始轴1上进行连接
concat_arr1 = np.concatenate([merge_arr1, merge_arr2], axis=1)
print(concat_arr1)
# (3, 8)
print(concat_arr1.shape)

# 新数组在原始轴0上进行连接
concat_arr2 = np.concatenate([merge_arr1, merge_arr2], axis=0)
print(concat_arr2)
# (6, 4)
print(concat_arr2.shape)
