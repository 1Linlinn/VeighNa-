import cv2

img_name = 'opencv_logo.png'

# 以彩色模式读取图像
im_bgr = cv2.imread(img_name, 1)
# 以灰度模式读取图像
im_gray = cv2.imread(img_name, 0)
# 连同图像的alpha通道一起读取
im_alpha = cv2.imread(img_name, -1)

# # 打印各个模式图像的数据类型以及形状
# print(type(im_bgr), im_bgr.shape)
# print(type(im_gray), im_gray.shape)
# print(type(im_alpha), im_alpha.shape)

# # 显示图像
# cv2.imshow('im_bgr', im_bgr)
# cv2.imshow('im_gray', im_gray)
# cv2.imshow('im_alpha', im_alpha)
# # 阻塞以防止窗口关闭
# cv2.waitKey(0)
# # 销毁所有图像显示窗口
# cv2.destroyAllWindows()
# # ====================================================
# print(ord('q') == cv2.waitKey(2000))
# # ====================================================
# 定义需要裁剪的子图大小
sub_h = sub_w = 100
# 获取原图像的形状
h, w = im_bgr.shape[: 2]

# 计算子图的左上角坐标
x = (w - sub_w) // 2
y = (h - sub_h) // 2

print(x, y)
# 切割子图，仅需要在空间上（前2维）切割，通道信息则全部保留（第3维）
sub_im = im_bgr[y: y + sub_h, x: x + sub_w, :]
print(sub_im.shape)
# 显示子图
cv2.imshow('sub_im', sub_im)
cv2.waitKey(0)
cv2.destroyAllWindows()
# ====================================================
import numpy as np

# 图像旋转
# 定义顺时针旋转角度
angle = 30

# 求旋转角度的正弦以及余弦值
sine = np.sin(angle / 180 * np.pi)
cosine = np.cos(angle / 180 * np.pi)

# 用于旋转的仿射矩阵
rotate_mat = np.array([[cosine, -sine, 0], [sine, cosine, 0]])
# 将旋转的仿射矩阵用于图像
rotate_im = cv2.warpAffine(im_bgr, rotate_mat, dsize=im_bgr.shape[: 2])
cv2.imshow('rotate', rotate_im)

# 使用OpenCV的api得到旋转矩阵，需要传入旋转中心，旋转角度（以逆时针旋转为正方向），缩放尺度
rotate_mat2 = cv2.getRotationMatrix2D((0, 0), -30, scale=1)
# 比较手动初始化的矩阵与api初始化的矩阵是否相同（True）
print(rotate_mat == rotate_mat2)

# 平移
shift_mat = np.array([[1., 0., 100.], [0., 1., 100.]])
shift_im = cv2.warpAffine(im_bgr, shift_mat, dsize=im_bgr.shape[: 2])
cv2.imshow('shift', shift_im)

# 缩放
scale_mat = np.array([[2., 0., 0.], [0., 2., 0.]])
scale_im = cv2.warpAffine(im_bgr, scale_mat, dsize=im_bgr.shape[: 2])
cv2.imshow('scale', scale_im)

# 翻转
flip_mat = np.array([[-1., 0., im_bgr.shape[0]], [0., 1., 0]])
flip_im = cv2.warpAffine(im_bgr, flip_mat, dsize=im_bgr.shape[: 2])
cv2.imshow('flip', flip_im)

# 竖直方向翻转（翻转代码为0）
cv2.flip(im_bgr, 0)
# 水平方向翻转（翻转代码为1）
cv2.flip(im_bgr, 1)
# 水平和竖直方向同时翻转（翻转代码为-1）
cv2.flip(im_bgr, -1)

# 拉伸
# 使用变换前后图像中发三个点确定仿射矩阵（getAffineTransform）
# [0, 0], [200, 200], [0, 100]为变换前图像中的三个点
pts1 = np.float32([[0, 0], [200, 200], [0, 100]])
# [100, 0], [100, 200], [50, 100]为变换后图像中对应的三个点
pts2 = np.float32([[100, 0], [100, 200], [50, 100]])

stre_mat = cv2.getAffineTransform(pts1, pts2)
print(stre_mat)

stre_im = cv2.warpAffine(im_bgr, stre_mat, dsize=im_bgr.shape[: 2])
cv2.imshow('stre', stre_im)

cv2.waitKey(0)
cv2.destroyAllWindows()