<template>

  <div id="container">
    <!-- 导航 -->
    <el-row>
      <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" background-color="#545c64"
        text-color="#fff" active-text-color="#ffd04b">
        <el-menu-item index="1"><a href="/#/SearchImg"> 相似图片</a></el-menu-item>
        <el-menu-item index="2"><a href="/#/Searchface"> 相似人脸</a></el-menu-item>
      </el-menu>
    </el-row>

    <!-- 图片上传 -->
    <el-row>
      <el-col :span="12">
        <el-upload class="img-uploader" :action="postUrl" :show-file-list="false" :on-success="handleUploadSuccess"
          :on-error="handlerError">
          <img v-if="uploadImgSrc" :src="uploadImgSrc" class="avatar">
          <i v-else class="el-icon-plus img-uploader-icon"></i>
        </el-upload>
      </el-col>
      <el-col :span="12">
          <el-link type="danger" icon="el-icon-refresh" :href="gindexUrl" target="_blank">重建人脸索引</el-link>
      </el-col>
    </el-row>



    <!-- 显示图片 -->
    <div id="img_container">
      <el-row>
        <!-- 遍历显示 -->
        <el-image v-for="(item, index) in imgUrls" :key="index" :src="item" :preview-src-list="imgUrls">
        </el-image>

      </el-row>

    </div>


  </div>



</template>

<script>
export default {
  name: 'SearchImg',
  data() {
    return {
      activeIndex: '2',
      uploadImgSrc: '',
      serverUrl: 'http://127.0.0.1:5000',
      gindexUrl: 'http://127.0.0.1:5000/manage/gfaceindex',
      postUrl: 'http://127.0.0.1:5000/api/face_search',
      imgUrls: []
    }
  },
  methods: {
    handleUploadSuccess(res, file) {
      // 解析返回的数据
      if (res['msg'] == 'noface') {
        this.$notify.error({
          title: '错误',
          message: '上传照片不包含人脸'
        });

      }
      if (res['msg'] == 'success') {
        this.imgUrls = res['urls']
        // 拼接图片地址
        this.imgUrls = this.imgUrls.map(item => {
          return this.serverUrl + item
        })

      }
      this.uploadImgSrc = URL.createObjectURL(file.raw);
    },

    handlerError(err, file) {
      // console.log(err, err);
      console.log('上传失败');
    },

  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#container a {
  text-decoration: none;

}
.el-link{
  margin-top: 80px;
  font-size: large;
}
.img-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 150px;
  height: 150px;
  margin-top: 10px;
}

.img-uploader :hover {
  border-color: #409EFF;
}

.img-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 150px;
  height: 150px;
  line-height: 150px;
  text-align: center;
}

.avatar {
  width: 150px;
  height: 150px;
  display: block;
}

#img_container {
  margin-top: 20px;
}

#img_container .el-image {
  width: 120px;
  /* min-height: 150px; */
  height: 120px;
  margin-bottom: 10px;
  margin-right: 10px;
}

#img_container .el-row {
  margin-bottom: 20px;
}

#img_container .el-col {
  margin-bottom: 10px;
}
</style>