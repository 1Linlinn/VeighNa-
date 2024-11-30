import matplotlib.pyplot as plt
import numpy as np

# 定义数据产生函数
def sin(start, end):
    # 使用np.linspace产生1000个等间隔的数据
    x = np.linspace(start, end, num=1000)
    return x, np.sin(x)

start = -10
end = 10

data_x, data_y = sin(start, end)

# 得到figure与axes对象，使用subplots默认只生成一个axes
figure, axes = plt.subplots()
axes.plot(data_x, data_y, label='Sin(x)')
# 显示plot中定义的label
axes.legend()
# 在图中显示网格
axes.grid()
# 设置图题
axes.set_title('Plot of Sin(x)')
# 显示图像
plt.show()

# ==========================================================
row = 2; col = 3
fig, axes = plt.subplots(row, col)
for i in range(row):
    for j in range(col):
        # 以索引的形式取出每一个axes
        axes[i][j].plot(data_x, data_y, label='Sin(x)')
        axes[i][j].set_title('Plot of Sin(x) at [{}, {}]'.format(i, j))
        axes[i][j].legend()
# 设置总图标题
plt.suptitle('All 2*3 plots')
plt.show()

# ==========================================================
# 从均值为0、标准差为1的正态分布引入小的噪声
noise_y = np.random.randn(*data_y.shape) / 2
noise_data_y = data_y + noise_y

figure, axes = plt.subplots()
# 使用散点图进行绘制
axes.scatter(data_x, noise_data_y, label='sin(x) with noise scatter')
axes.grid()
axes.legend()
plt.show()

# ==========================================================
# 生成10000个正态分布中的数组
norm_data = np.random.normal(size=[10000])
figure, axes = plt.subplots(1, 2)
# 将数据分置于10个桶中
axes[0].hist(norm_data, bins=10, label='hist')
axes[0].set_title('Histogram with 10 bins')
axes[0].legend()
# 将数据分置于1000个桶中
axes[1].hist(norm_data, bins=1000, label='hist')
axes[1].set_title('Histogram with 1000 bins')
axes[1].legend()
plt.show()

# ==========================================================
figure, axes = plt.subplots()
axes.bar(data_x, data_y, label='bar')
axes.legend()
axes.grid()
plt.show()

# ==========================================================
figure, axes = plt.subplots()
# 绘制曲线图
axes.plot(data_x, data_y, label='Sin(x)', linewidth=5)
# 绘制散点图，此时axes对象仍处于活动状态，直接绘制即可
axes.scatter(data_x, noise_data_y, label='scatter noise data', color='yellow')
axes.legend()
axes.grid()
plt.show()

# ==========================================================
figure, axes = plt.subplots()
# 定义时间的长度
num = 100

# 定义带系数的正弦函数，以模拟不同时刻的数据
def sin_with_effi(start, end, effi):
    x = np.linspace(start, end, num=1000)
    return x, np.sin(effi * x)

# 打开Matplotlib的交互绘图模式
plt.ion()

# 对时间长度进行循环
for i in range(num):
    # 清除上一次绘图结果
    plt.cla()
    # 取出当前时刻的数据
    data_x, data_y = sin_with_effi(start, end, effi=i / 10)
    axes.plot(data_x, data_y)
    # 暂停图像以显示最新结果
    plt.pause(0.001)

# 关闭交互模式
plt.ioff()
# 显示最终结果
plt.show()

# ==========================================================
img_path = 'matplotlib_logo.png'
# 读取图像
img = plt.imread(img_path)
# 将图像置于figure上
plt.imshow(img)
plt.show()

# ==========================================================
row = col = 256
# 定义一个空的占位符
heatmap = np.empty(shape=[row, col])
# 初始化占位符中每一个像素
for i in range(row):
    for j in range(col):
        heatmap[i][j] = np.random.rand() * i + j
# imshow将输入的图像进行归一化并映射至0-255，较小值使用深色表示，较大值使用浅色表示
plt.imshow(heatmap)
plt.show()