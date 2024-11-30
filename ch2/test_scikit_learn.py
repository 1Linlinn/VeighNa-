from sklearn.svm import SVR, SVC
import numpy as np
import matplotlib.pyplot as plt

# 生成回归任务的数据
def get_regression_data():
    start = -10
    end = 10
    space = 0.01

    # 自变量从[start, end]中以space为等间距获取
    x = np.linspace(start, end, int((end - start) / space))
    # 根据自变量计算因变量，并给其加上噪声干扰
    y = x * np.sin(x) + 0.1 * x ** 2 * np.cos(x) + x + 5 * np.random.randn(*x.shape)
    
    # 返回训练数据
    return np.reshape(x, [-1, 1]), y

# 得到回归数据
x, y = get_regression_data()
# 打印数据形状以进行验证
print(x.shape, y.shape)

# 可视化数据
figure, axes = plt.subplots()

# 以散点图绘制数据
axes.scatter(x, y, s=1, label='training data')
# 以latex风格设置标题
axes.set_title('$y=x sin(x) + 0.1x^2 cos(x) + x$')
axes.legend()
axes.grid()
plt.show()

# 初始化分类模型
svr = SVR(kernel='rbf', C=10)

# 用模型对数据进行拟合
svr_fit = svr.fit(x, y)

# 使用模型进行测试
svr_predict = svr_fit.predict(x)

# 可视化模型学到的曲线
fig, axes = plt.subplots()
axes.scatter(x, y, s=1, label='training data')
axes.plot(x, svr_predict, lw=2, label='rbf model', color='red')
axes.legend()
axes.grid()
plt.show()

# 评估模型性能
score = svr_fit.score(x, y)
print(score)

# =================================================================
# 生成分类任务的数据
def get_classification_data():
    # 数据量
    cnt_num = 1000
    # 计数器
    num = 0

    # 初始化数据与标签的占位符，其中训练数据为平面上的坐标，标签为类别号
    x = np.empty(shape=[cnt_num, 2])
    y = np.empty(shape=[cnt_num])

    while num < cnt_num:
        # 生成随机的坐标值
        rand_x = np.random.rand() * 4 - 2
        rand_y = np.random.rand() * 4 - 2

        # 非法数据，超出了x^2 + y^2 = 4的圆的范围，重新生成合法坐标
        while rand_x ** 2 + rand_y ** 2 > 4:
            rand_x = np.random.rand() * 4 - 2
            rand_y = np.random.rand() * 4 - 2

        # 如果生成的坐标在x^2 / 1.5^2 + y^2 = 1的椭圆范围内，则类标号为0；否则为1
        if rand_x ** 2 / 1.5 ** 2 + rand_y ** 2 <= 1:
            label = 0
        else:
            label = 1
        
        # 将坐标存入占位符
        x[num][0] = rand_x
        x[num][1] = rand_y
        
        # 将标签存入占位符
        y[num] = label

        num += 1
    
    # 给训练数据添加随机扰动以模拟真实数据
    x += 0.3 * np.random.randn(*x.shape)
    
    return x, y

# 得到训练数据与标签
x, y = get_classification_data()
# 查看数据和标签的形状
print(x.shape, y.shape)

# 获取标签为0的数据下标
zero_cord = np.where(y == 0)
# 获取标签为1的数据下标
one_cord = np.where(y == 1)

# 以下标取出标签为0的训练数据
zero_class_cord = x[zero_cord]
# 以下标取出标签为1的训练数据
one_class_cord = x[one_cord]

figure, axes = plt.subplots()
# 以圆点画出标签为0的训练数据
axes.scatter(zero_class_cord[:, 0], zero_class_cord[:, 1], s=15, marker='o', label='class 0')
# 以十字画出标签为1的训练数据
axes.scatter(one_class_cord[:, 0], one_class_cord[:, 1], s=15, marker='+', label='class 1')
axes.grid()
axes.legend()

# 分别打印标签为0和1的训练数据的形状
print(zero_class_cord.shape, one_class_cord.shape)
plt.show()

# 创建SVM模型
clf = SVC(C=100)

clf.fit(x, y)

def border_of_classifier(sklearn_cl, x):
    # 求出所关心范围的最边界值：最小的x、最小的y、最大的x、最大的y
    x_min, y_min = x.min(axis = 0) - 1
    x_max, y_max = x.max(axis = 0) + 1

    # 将[x_min, x_max]和[y_min, y_max]这两个区间分成足够多的点（以0.01为间隔）
    x_values, y_values = np.meshgrid(np.arange(x_min, x_max, 0.01), np.arange(y_min, y_max, 0.01))

    # 将上一步分隔的x与y值使用np.stack两两组成一个坐标点，覆盖整个关心的区域
    mesh_grid = np.stack((x_values.ravel(), y_values.ravel()), axis=-1)

    # 使用训练好的模型对于上一步得到的每一个点进行分类，得到对应的分类结果
    mesh_output = sklearn_cl.predict(mesh_grid)

    # 改变分类输出的形状，使其与坐标点的形状相同（颜色与坐标一一对应）
    mesh_output = mesh_output.reshape(x_values.shape)
    
    fig, axes = plt.subplots()
    
    # 根据分类结果从 cmap 中选择颜色进行填充（为了图像清晰，此处选用binary配色）
    axes.pcolormesh(x_values, y_values, mesh_output, cmap='binary')
    
    # 将原始训练数据绘制出来
    axes.scatter(zero_class_cord[:, 0], zero_class_cord[:, 1], s=15, marker='o', label='class 0')
    axes.scatter(one_class_cord[:, 0], one_class_cord[:, 1], s=15, marker='+', label='class 1')
    axes.legend()
    axes.grid()
    
    plt.show()

# 绘制分类器的边界，传入已训练好的分类器，以及训练数据（为了得到关心的区域范围）
border_of_classifier(clf, x)

# 评估模型性能
score = clf.score(x, y)
print(score)
