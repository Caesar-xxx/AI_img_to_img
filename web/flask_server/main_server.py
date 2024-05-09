from flask import Flask, redirect, url_for, request
from flask_cors import CORS
from flask import jsonify
import cv2
import numpy as np

from face_utils import FaceUtils
from img_utils import ImgUtils
# 实例化
face_helper = FaceUtils()
img_helper = ImgUtils()


app = Flask(__name__)
CORS(app) # 跨域访问

@app.route('/manage/gfaceindex',methods = [ 'GET'])
def gfaceindex():
    '''
    重新生成人脸索引
    '''
    face_helper.generateFaceIndex()
    return "<p>generated index!</p>"

@app.route('/manage/gimgindex',methods = [ 'GET'])
def gimgindex():
    '''
    重新生成图片索引
    '''
    img_helper.generateImgIndex()
    return "<p>generated index!</p>"
    
    
@app.route('/api/img_search',methods = ['POST', 'GET'])
def img_search():

    '''
    上传图片搜索相似图片
    1.接受文件
    2.预处理
    3.查询图片的特征
    4.faiss查询结果
    5.返回URL
    '''
    if request.method == 'POST':
        # 1.接受文件
        f = request.files['file']
        # 2.保存
        img_path = 'uploaded_file/'+f.filename
        f.save(img_path)
        # 3.获取特征
        post_feat = img_helper.getFeature(img_path)
        # 4.搜索
        img_paths = img_helper.searchImages(post_feat,100)
        
        back_data = {
            'msg': 'success',
            'urls': img_paths
        }

        return back_data
    else:
        return "<p>Denied!</p>"

@app.route('/api/face_search',methods = ['POST', 'GET'])
def face_search():

    '''
    上传图片搜索相似人脸
    1.接受文件
    2.裁剪人脸
    3.查询图片的特征
    4.faiss查询结果
    5.返回URL
    '''
    if request.method == 'POST':
        # 1.recieve file
        f = request.files['file']
        # 2.save file
        img_path = 'uploaded_file/'+f.filename
        f.save(img_path)
        # 3.裁剪人脸
        croped_face = face_helper.getCropedFace(img_path)
        if croped_face is  None:
            return {'msg': 'noface'}
        # 4.保存裁剪后的人脸
        cv2.imencode('.jpg', croped_face)[1].tofile(img_path) 
        # 4.获取特征
        post_feat = face_helper.getFaceEmbedding(img_path)
        # 5.搜索
        img_paths = face_helper.searchFaces(post_feat,100)
        
        back_data = {
            'msg': 'success',
            'urls': img_paths
        }

        return back_data
    else:
        return "<p>Denied!</p>"


# 启动服务
app.run(host='0.0.0.0', port=5000)