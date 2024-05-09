'''
人脸辅助类
功能：
1.获取embedding
2.生成所有人脸索引
    A.遍历所有origin下的人脸图片
    B.裁剪人脸并保存至croped文件夹
    C.获取图片特征（通过API）
    D.保存索引文件
'''
import requests
import numpy as np
import faiss
import glob
import tqdm
import cv2
import os

class FaceUtils:
    def __init__(self):
        # 加载人脸检测模型
        self.face_detector = cv2.dnn.readNetFromCaffe('./weights/deploy.prototxt.txt','./weights/res10_300x300_ssd_iter_140000.caffemodel')
        # 判断文件夹是否存在
        if not os.path.exists('./indexs/faces.index'):
            # 如果不存在，则生成索引文件
            print('人脸索引文件不存在，将生成索引')
            self.generateFaceIndex()
                
        self.face_index = faiss.read_index('./indexs/faces.index')
        # 人员名称列表
        self.name_list = np.load('./indexs/face_name_list.npy')


    def getCropedFace(self,img_file, conf_thresh=0.5 ):
        """
        将图片进行人脸裁剪
        """
        # 读取图片
        # img = cv2.imread(img_file)
        # 解决中文路径问题
        img=cv2.imdecode(np.fromfile(img_file,dtype=np.uint8),-1)
        if img is None:
            return None
        # 画面原来高度和宽度
        img_height,img_width = img.shape[:2]
        # 缩放图片
        img_resize = cv2.resize(img,(300,300))
        # PNG 图片不支持读取，需要转换为jpg
        if img_resize.shape[2] == 4:
            img_resize = cv2.cvtColor(img_resize,cv2.COLOR_BGRA2BGR)
        # 图像转为blob
        img_blob = cv2.dnn.blobFromImage(img_resize,1.0,(300,300),(104.0, 177.0, 123.0))
        # 输入
        self.face_detector.setInput(img_blob)
        # 推理
        detections = self.face_detector.forward()
        # 查看检测人脸数量
        num_of_detections = detections.shape[2]
        # 遍历人脸
        for index in range(num_of_detections):
            # 置信度
            detection_confidence = detections[0,0,index,2]
            # 挑选置信度，找到一个人返回
            if detection_confidence > conf_thresh:
                # 位置
                locations = detections[0,0,index,3:7] * np.array([img_width,img_height,img_width,img_height])
                # 矩形坐标
                l,t,r,b  = locations.astype('int')
                croped_face = img[t:b,l:r]
                return croped_face
                    
        # 都不满足
        return None

    def generateCropedFace(self):
        '''
        保存裁剪后的人脸图片
        '''
        # 获取人名列表
        person_list = glob.glob('./static/images/faces/origin/*')
        # 遍历人名
        for img_file in tqdm.tqdm( person_list , desc='裁剪人脸，保存至croped文件夹'):
            # 处理图片
            croped_face = self.getCropedFace(img_file)
            if croped_face is not None:
                # 获取文件名（这里需要根据自己系统来改一下，Windows用os.sep，Unix系系统用/））
                file_name = img_file.split(os.sep)[-1]
                # 保存，同样要解决中文路径
                save_file_name = './static/images/faces/croped/'+file_name
                cv2.imencode('.jpg', croped_face)[1].tofile(save_file_name) 
                

        
    def getFaceEmbedding(self,fileName):
        '''
        传入文件名，通过API获取人脸embedding

        '''
        url = "http://host.docker.internal:8080/predictions/facenet"
        with open(fileName, 'rb') as img:
            payload = img
            headers = {
            'Content-Type': 'image/jpeg'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            result = np.array(response.json()['res'])
            return result

    def generateFaceIndex(self):
        '''
        生成所有人脸索引
        '''
        # 遍历所有人脸图片
        known_face_list = glob.glob('./static/images/faces/croped/*')

        if len(known_face_list) == 0:
            print('croped下没有人脸图片，即将重新裁剪')
            self.generateCropedFace()
            known_face_list = glob.glob('./static/images/faces/croped/*')

        # 记录名字
        name_list = []
        # 网络embedding
        net_embedding = []
        # 遍历
        for face in tqdm.tqdm(known_face_list, desc='获取人脸embedding'):
            name = face.split(os.sep)[-1].split('.')[0]
            name_list.append(name)
            net_embedding.append(self.getFaceEmbedding(face))
        # feat_list转为numpy数组
        feat_array = np.array(net_embedding)
        # 转为float32
        feat_array = feat_array.astype(np.float32)
        # faiss创建图片特征索引
        index = faiss.IndexFlatL2(128)
        # 将图片特征、id加入索引
        index.add(feat_array)
        # 保存索引
        faiss.write_index(index, './indexs/faces.index')
        # 输出信息
        print('索引保存完毕，共生成了%d个索引' % index.ntotal)
        
        # 保存名字为numpy数组文件
        np.save('./indexs/face_name_list.npy', name_list)
        # 输出信息
        print('名字保存完毕，共生成了%d个名字' % len(name_list))

    def searchFaces(self,post_feat, top_k=10):
        '''
        搜索人脸
        '''
        # 扩张维度
        feat = np.expand_dims(post_feat, axis=0)
        # float32
        feat = feat.astype(np.float32)
        # 搜索
        D, I = self.face_index.search(feat, top_k) # 
        # 获取图片路径
        query_file_name = self.name_list[I[0]]
        # 包装文件名
        img_paths = []
        for filename in query_file_name:
            img_name = '/static/images/faces/origin/' + filename + '.jpg' 
            img_paths.append(img_name)   

        return img_paths

# # 实例化
# face =  FaceUtils()
# face.generateCropedFace()
# face.generateFaceIndex()