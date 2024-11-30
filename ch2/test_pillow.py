from PIL import Image
import numpy as np

img_name = 'pillow_logo.jpg'
# 使用open方法读取图像
rgb_im = Image.open(img_name)
# 显示图像
# rgb_im.show()
# 显示图像的格式及其大小（宽度，高度）
print(rgb_im.mode, rgb_im.size)

# 图像格式转换函数
def convert(im, mode):
    # 将图像转换为mode格式
    im = im.convert(mode)
    im.show()
    # 取出图像中的一个像素，以便查看其类型
    pixel = im.getpixel((0, 0))
    # 查看特定mode下图像相关信息
    print(im.mode, im.size, pixel, type(pixel))
    im.close()

# 待查看的mode
modes = ['1', 'L', 'RGBA', 'I', 'F']

for m in modes:
    # convert(rgb_im, m)
    input()
# ==================================================
from PIL import ImageEnhance

# 待测试的饱和度调节因子
color_factors = [0, 0.5, 1, 10]
# 创建Color对象
color_im = ImageEnhance.Color(rgb_im)
for cf in color_factors:
    # 显示增强后的图像
    # color_im.enhance(cf).show()
    # input()
    pass
# ==================================================
# 待测试的对比度调节因子
contrast_factors = [0, 0.5, 1, 10]
# 创建Contrast对象
contrast_im = ImageEnhance.Contrast(rgb_im)
for cf in contrast_factors:
    # 显示增强后的图像
    # contrast_im.enhance(cf).show()
    # input()
    pass
# ==================================================
# 待测试的亮度调节因子
brightness_factors = [0, 0.5, 1, 10]
# 创建Brightness对象
brightness_im = ImageEnhance.Brightness(rgb_im)
for bf in brightness_factors:
    # 显示增强后的图像
    # brightness_im.enhance(bf).show()
    # input()
    pass
# ==================================================
# 待测试的锐度调节因子
sharpness_factors = [0, 0.5, 1, 10]
# 创建Sharpness对象
sharpness_im = ImageEnhance.Sharpness(rgb_im)
for sf in sharpness_factors:
    # 显示增强后的图像
    # sharpness_im.enhance(sf).show()
    # input()
    pass
# ==================================================
from PIL import ImageOps

# 待测试的裁剪宽度
crop_borders = [0, 10, 20, 50]

for cb in crop_borders:
    # 为crop函数传入待裁剪图像以及裁剪宽度
    crop_im = ImageOps.crop(rgb_im, cb)
    # 打印裁剪后图像的大小
    print(crop_im.size)
    # 显示裁剪后的图像
    # crop_im.show()
    # input()
    pass
# ==================================================
# 待测试的缩放因子
scale_factors = [0.1, 0.3, 0.5, 0.7]

for sf in scale_factors:
    # 为scale函数传入待缩放图像以及缩放因子
    scale_im = ImageOps.scale(rgb_im, sf)
    # 打印缩放后图像的大小
    print(scale_im.size)
    # 显示缩放后的图像
    # scale_im.show()
    # input()
    pass
# ==================================================
# 竖直翻转图像
flip_im = ImageOps.flip(rgb_im)
# flip_im.show()

# 水平翻转图像
mirror_im = ImageOps.mirror(rgb_im)
# mirror_im.show()
# ==================================================
# 旋转角度
rotate_angle = 45

# # 将图像逆时针旋转45°
# rgb_im.rotate(rotate_angle).show()
# # 设置图像旋转中心为左上角，并逆时针旋转45°
# rgb_im.rotate(rotate_angle, center=(0, 0)).show()
# # 将图像逆时针旋转45°并以白色填充缺失部分
# rgb_im.rotate(rotate_angle, fillcolor='white').show()
# # 扩展图像边界以容纳所有图像信息
# rgb_im.rotate(rotate_angle, expand=1).show()
# ==================================================
# 使图像反色
# ImageOps.invert(rgb_im).show()
# ==================================================
# 图像像素保留位数
posterize_bits = [1, 2, 4, 8]

for pb in posterize_bits:
    posterized_im = ImageOps.posterize(rgb_im, bits=pb)
    # 显示图像
    # posterized_im.show()
    # 查看图像左上角的像素
    pixel = posterized_im.getpixel((0, 0))
    # 打印左上角像素及其对应的二进制值
    print(pixel, bin(pixel[0]))
# ==================================================
# 图像solarize像素参数
solarize_thresh = [127, 255]

for st in solarize_thresh:
    # solarize方法
    solarized_im = ImageOps.solarize(rgb_im, threshold=st)
    solarized_im.show()
    
    # invert方法
    invert_im = ImageOps.invert(rgb_im)
    invert_im.show()
    # input()
    # 对比原图、solarize以及invert图像中的像素
    print(rgb_im.getpixel((400, 400)), solarized_im.getpixel((400, 400)), invert_im.getpixel((400, 400)))
# ==================================================
# 导入Matplotlib以绘制直方图
import matplotlib.pyplot as plt

# 直方图均衡化
equalized_im = ImageOps.equalize(rgb_im)

# 将图像转换为灰度图并得到直方图数据（在此仅考虑灰度图直方图）
# 原图像直方图
rgb_hist = rgb_im.convert('L').histogram()
# 均衡化后图像直方图
equalized_hist = equalized_im.convert('L').histogram()

# 绘制图像及其对应的直方图
figure, axes = plt.subplots(1, 4)

axes[0].imshow(rgb_im)
axes[0].set_title('Original image')
axes[1].bar(range(len(rgb_hist)), rgb_hist)
axes[1].set_title('Original histogram')
axes[2].imshow(equalized_im)
axes[2].set_title('Equalized image')
axes[3].bar(range(len(equalized_hist)), equalized_hist)
axes[3].set_title('Equalized histogram')

# plt.show()
