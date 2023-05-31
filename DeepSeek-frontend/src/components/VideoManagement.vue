<template>
  <div>
    <el-button type="primary" @click="addDialogFormVisible = !addDialogFormVisible"
               style="margin-bottom: 10px; margin-right: 20px; background-color: #70a1ff">上传视频
    </el-button>
    <!--  添加视频信息弹窗  -->
    <el-dialog title="上传视频" :visible.sync="addDialogFormVisible">
      <el-upload
        ref="upload"
        :action="uploadUrl"
        :before-upload="beforeUpload"
        :on-success="onSuccess"
        :on-error="onError"
        :file-list="fileList"
        :headers="headerObj"
        :show-file-list="true"
        class="upload-demo">
        <el-button slot="trigger" size="small" type="primary">选取文件</el-button>
        <div slot="tip" class="el-upload__tip">只能上传mp4格式的文件</div>
      </el-upload>
      <el-form ref="form" :model="form" label-width="80px" style="margin-top: 20px">
        <el-form-item label="名称">
          <el-input v-model="form.title"></el-input>
        </el-form-item>
        <el-form-item label="文案">
          <el-input type="textarea" :rows="3" v-model="form.description"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm">提交</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
    <!-- 信息表格   -->
    <el-table
      :data="tableData"
      border
      style="width: 100%">
      <el-table-column
        prop="videoNum"
        label="编号"
        min-width=10%>
      </el-table-column>
      <el-table-column
        prop="name"
        label="名称"
        min-width=25%>
      </el-table-column>
      <el-table-column
        prop="owner"
        label="上传者"
        min-width=35%>
      </el-table-column>
      <el-table-column
        prop="uploadTime"
        label="上传时间"
        min-width=30%>
      </el-table-column>
      <el-table-column
        label="操作"
        min-width=10%>
        <template slot-scope="scope">
          <el-button @click="videoDetail(scope.row, scope.$index)" type="text" size="small">详 情</el-button>
          <el-button type="text" size="small" @click="handleDelete(scope.row, scope.$index)">删 除</el-button>
          <el-dialog title="详情" :visible.sync="scope.row.isDetail" @close="outClose(scope.row)">
            <el-descriptions class="margin-top" :column="1" border>
              <el-descriptions-item>
                <template slot="label">
                  <i class="el-icon-position"></i>
                  编号
                </template>
                <span>{{scope.row.videoNum}}</span>
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label">
                  <i class="el-icon-price-tag"></i>
                  名称
                </template>
                <span>{{scope.row.name}}</span>
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label">
                  <i class="el-icon-postcard"></i>
                  上传者
                </template>
                <span>{{scope.row.owner}}</span>
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label">
                  <i class="el-icon-time"></i>
                  上传时间
                </template>
                <span>{{scope.row.uploadTime}}</span>
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label">
                  <i class="el-icon-toilet-paper"></i>
                  文案
                </template>
                <span>{{scope.row.description}}</span>
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label">
                  <i class="el-icon-video-camera"></i>
                  视频
                </template>
                <video ref="videoPlayer" :src="require('../../public/videos/' + scope.row.owner + '/' + scope.row.url)" controls></video>
              </el-descriptions-item>
            </el-descriptions>
          </el-dialog>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import axios from 'axios'
import baseApiUrl from '../../config.default'

export default {
  name: 'VideoManagement',
  data () {
    return {
      fileList: [],
      hashList: [],
      form: {
        title: '',
        description: ''
      },
      uploadUrl: baseApiUrl + '/upload',
      loading: false,
      headerObj: {
        Authorization: localStorage.getItem('token')
      },
      addDialogFormVisible: false,
      updateDialogFormVisible: [],
      tableData: [],
      searchStr: '',
      queryMethod: '编号',
      queryCol: 'videoNum'
    }
  },
  mounted () {
    this.selectMyVideos()
  },
  methods: {
    handleCommand (command) {
      this.queryCol = command
      switch (command) {
        case 'videoNum':
          this.queryMethod = '编号'
          break
        case 'name':
          this.queryMethod = '名称'
          break
        case 'owner':
          this.queryMethod = '上传者'
          break
      }
    },
    selectMyVideos () {
      this.tableData = []
      const url = `${baseApiUrl}/getvideos/my`
      // 获取数据库全部视频列表
      axios.get(url, {
        headers: {
          Authorization: localStorage.getItem('token')
        }
      }).then(rs => {
        if (rs.status === 200) {
          console.log('rs:' + rs.data)
          rs.data.forEach(item => { this.tableData.push(item) })
        }
      }).catch(error => {
        if (error.response.status === 401) {
          this.$message.error(error.response.data.message)
          this.$router.push('/')
        }
      })
    },
    videoDetail: function (row, i) {
      row.isDetail = true
    },
    outClose: function (row) {
      row.isDetail = false
      this.$refs.videoPlayer.pause()
    },
    sleep: function () {
      var timeStamp = new Date().getTime()
      var endTime = timeStamp + 500
      while (true) {
        if (new Date().getTime() > endTime) {
          return
        }
      }
    },
    submitForm () {
      this.$message('正在上传')
      const data = new FormData()
      data.append('title', this.form.title)
      data.append('description', this.form.description)
      data.append('hash', this.hashList[0].hash)
      data.append('fmt', this.hashList[0].fmt)
      const url = `${baseApiUrl}/upload`
      axios.post(url, data, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: localStorage.getItem('token')
        }
      }).then(rs => {
        console.log('promise-rs:', rs)
        if (rs.status === 206) {
          this.$alert('存在相似度较高片段，建议您检查后再上传一次', '提示')
        }
        this.$message.success('上传成功')
        // this.tableData = rs.data.data
        this.selectMyVideos()
      }).catch(() => {
        this.$message.close()
        this.$message.error('上传失败')
      })
      this.addDialogFormVisible = false
      this.fileList = []
      this.hashList = []
    },
    beforeUpload (file) {
      const isMp4 = file.type === 'video/mp4'
      const isLt100M = file.size / 1024 / 1024 < 100
      if (!isMp4) {
        this.$message.error('只能上传mp4格式的视频')
      }
      if (!isLt100M) {
        this.$message.error('上传视频大小不能超过 100MB')
      }
      return isMp4 && isLt100M
    },
    onSuccess (response, file) {
      // console.log(response)
      this.hashList.push({
        name: file.name,
        hash: response.hash,
        fmt: response.fmt
      })
      // console.log(this.hashList[0])
      // this.$message.success('上传成功')
    },
    onError (file) {
      this.$message.error('上传失败')
    },
    handleDelete: function (row, i) {
      console.log(row.name)
      this.$confirm('该操作将删除一个视频，是否确定？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        console.log('删除：' + row.videoNum)
        const formData = new FormData()
        formData.append('videoNum', row.videoNum)
        const url = `${baseApiUrl}/delete`
        axios.post(url, formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            Authorization: localStorage.getItem('token')
          }
        }).then(rs => {
          console.log('promise-rs:', rs)
          this.tableData.splice(i, 1)
          this.$message.success('删除成功')
        }).catch(() => {
          this.$message.error('删除失败')
        })
      })
    }
  }
}
</script>

<style>
  video{
    width:600px;
    height:400px;
  }
</style>
