'''
图片辅助类
1.获取特征
2.建立索引

'''
import requests
import numpy as np
import faiss
import glob
import tqdm
import cv2
import os

import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
# process_input
from tensorflow.keras.applications.vgg16 import preprocess_input


class ImgUtils:
    def __init__(self):
        # 判断文件是否存在
        if not os.path.exists('./indexs/voc.index'):
            print('图片索引文件不存在，将生成索引')
            self.generateImgIndex()
        # 读取索引
        self.img_index = faiss.read_index('./indexs/voc.index')
        # numpy从文件中读取文件名
        self.img_name_list = np.load('./indexs/voc_name_list.npy')
       

    def imgProcess(self,img_path):
        '''
        图片预处理
        '''
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        return x

    def getFeature(self,imageFile):
        '''
        获取图片特征
        '''
        image = self.imgProcess(imageFile)

        image_tensor = image.tolist()
        url = "http://host.docker.internal:8501/v1/models/vgg16:predict"

        json_data = {
            "instances": image_tensor
        }
        # 发送请求
        response = requests.post(url, json=json_data)
        # 解析结果
        result = np.array(response.json()['predictions'])[0]
        # 归一化
        post_feat = result/np.linalg.norm(result)
        return post_feat

    def generateImgIndex(self):
        '''
        生成图片索引
        '''
        # 遍历所有图片
        known_img_list = glob.glob('./static/images/voc/JPEGImages/*')
        if len(known_img_list) == 0:
            print('没有图片')
            return

        # 记录名字
        name_list = []
        # 网络embedding
        net_embedding = []
        # 遍历
        for img_file in tqdm.tqdm(known_img_list, desc='获取图片特征'):
            name = img_file.split(os.sep)[-1].split('.')[0]
            name_list.append(name)
            net_embedding.append(self.getFeature(img_file))
        # feat_list转为numpy数组
        feat_array = np.array(net_embedding)
        # 转为float32
        feat_array = feat_array.astype(np.float32)
        # faiss创建图片特征索引
        # 索引维度
        d = feat_array.shape[1]
        index = faiss.IndexFlatL2(d)
        # 将图片特征、id加入索引
        index.add(feat_array)
        # 保存索引
        faiss.write_index(index, './indexs/voc.index')
        # 输出信息
        print('索引保存完毕，共生成了%d个索引' % index.ntotal)
        
        # 保存名字为numpy数组文件
        np.save('./indexs/voc_name_list.npy', name_list)
        # 输出信息
        print('名字保存完毕，共生成了%d个名字' % len(name_list))


    def searchImages(self,post_feat, top_k=10):
        '''
        搜索图片
        '''
        # 扩张维度
        feat = np.expand_dims(post_feat, axis=0)
        # float32
        feat = feat.astype(np.float32)
        # 搜索
        D, I = self.img_index.search(feat, top_k) # 
        # 获取图片路径
        query_file_name = self.img_name_list[I[0]]
        # 包装文件名
        img_paths = []
        for filename in query_file_name:
            img_name = '/static/images/voc/JPEGImages/' + filename + '.jpg' 
            img_paths.append(img_name)   

        return img_paths
