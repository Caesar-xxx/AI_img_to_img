'''
提取特征的类
'''
# 导入相关包
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 导入TensorFlow    
import tensorflow as tf
# 导入vgg16
from tensorflow.keras.applications.vgg16 import VGG16

# 从tf keras 下导入预处理模块
from tensorflow.keras.preprocessing import image
# 导入preprocess_input
from tensorflow.keras.applications.vgg16 import preprocess_input


class FeatureExtract:
    def __init__(self):
        # 初始化vgg16模型
        self.vgg16 = VGG16(weights='imagenet', include_top=False,pooling='avg',input_shape=(224,224,3))
    
    # 提取图片特征的函数
    def extractFeat(self,fileName):
        # 加载图片
        img = image.load_img(fileName, target_size=(224, 224))
        # 转为numpy数组
        img_array = image.img_to_array(img)
        # 扩张维度
        img_array = np.expand_dims(img_array, axis=0)
        # 预处理
        img_array = preprocess_input(img_array)

        # 输入模型进行特征提取
        feat = self.vgg16.predict(img_array)
        # L2归一化
        feat = feat[0] / np.linalg.norm(feat[0])

        return feat
