<template>
  <div>
    <el-dropdown @command="handleCommand">
      <el-button type="primary" style="background-color: #70a1ff; width: 90%; margin-bottom: 10px;">
        {{queryMethod}}<i class="el-icon-arrow-down el-icon--right"></i>
      </el-button>
      <el-dropdown-menu slot="dropdown">
        <el-dropdown-item command="videoNum">编号</el-dropdown-item>
        <el-dropdown-item command="name">名称</el-dropdown-item>
        <el-dropdown-item command="owner">上传者</el-dropdown-item>
      </el-dropdown-menu>
    </el-dropdown>
    <el-input v-model="searchStr" placeholder="搜索视频" style="width: 60%">
      <el-button type="primary" slot="append" icon="el-icon-search" @click="queryInfo()">搜索</el-button>
    </el-input>
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
          <el-button @click="videoDetail(scope.row)" type="text" size="small">详 情</el-button>
          <el-button type="text" size="small" @click="enterCompare(scope.row)">比 较</el-button>
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
                <video ref="videoplayer" :src="require('../../public/videos/' + scope.row.owner + '/' + scope.row.url)" controls></video>
              </el-descriptions-item>
            </el-descriptions>
          </el-dialog>
          <el-dialog title="选择要比较的视频" :visible.sync="addDialogFormVisible">
            <el-form ref="form" :model="form" label-width="80px" style="margin-top: 20px">
              <el-form-item label="视频名称">
                <el-select v-model="select" filterable placeholder="请选择">
                  <el-option
                    v-for="item in myData"
                    :key="item.id"
                    :label="item.name"
                    :value="item.url">
                  </el-option>
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="compareVideo()">提交</el-button>
              </el-form-item>
            </el-form>
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
  name: 'VideoInfo',
  data () {
    return {
      fileList: [],
      hashList: [],
      targetfile: '',
      targetowner: '',
      form: {
        title: '',
        description: ''
      },
      headerObj: {
        Authorization: localStorage.getItem('token')
      },
      addDialogFormVisible: false,
      updateDialogFormVisible: false,
      tableData: [],
      myData: [],
      select: '',
      searchStr: '',
      queryMethod: '编号',
      queryCol: 'videoNum'
    }
  },
  mounted () {
    this.selectAllVideos()
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
    enterCompare: function (row) {
      this.targetfile = row.url
      this.targetowner = row.owner
      this.selectMyVideos()
      this.addDialogFormVisible = true
    },
    selectMyVideos () {
      this.myData = []
      const url = `${baseApiUrl}/getvideos/my`
      // 获取数据库全部视频列表
      axios.get(url, {
        headers: {
          Authorization: localStorage.getItem('token')
        }
      }).then(rs => {
        if (rs.status === 200) {
          console.log('rs:' + rs.data)
          rs.data.forEach(item => { this.myData.push(item) })
        }
      }).catch(error => {
        if (error.response.status === 401) {
          this.$message.error(error.response.data.message)
          this.$router.push('/')
        }
      })
    },
    selectAllVideos () {
      this.tableData = []
      const url = `${baseApiUrl}/getvideos/all`
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
    compareVideo: function () {
      const yourfile = this.select
      // const targetfile = row.url
      // const targetowner = row.owner
      // this.selectMyVideos()
      // this.addDialogFormVisible = true
      const data = new FormData()
      console.log(this.targetfile)
      console.log(this.targetowner)
      data.append('yourfile', yourfile)
      data.append('targetfile', this.targetfile)
      data.append('targetowner', this.targetowner)
      const url = `${baseApiUrl}/compare`
      axios.post(url, data, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: localStorage.getItem('token')
        }
      }).then(rs => {
        if (rs.status === 206) {
          this.$message.error('您的剩余使用次数不足，请及时充值')
        } else if (rs.status === 200) {
          this.$message.success('请求成功，稍后可在日志中查看结果')
          console.log('promise-rs:', rs)
          // this.tableData = rs.data.data
          this.selectMyVideos()
        }
      }).catch(() => {
        this.$message.error('请求失败')
      })
      this.addDialogFormVisible = false
      this.myData = []
    },
    videoDetail: function (row, i) {
      row.isDetail = true
    },
    outClose: function (row) {
      row.isDetail = false
      this.$refs.videoplayer.pause()
    },
    queryInfo () {
      if (this.searchStr) {
        const queryData = this.queryCol + '=' + this.searchStr
        console.log(queryData)
        const url = `${baseApiUrl}/getvideos/query?` + queryData
        console.log('url:' + url)
        axios.get(url, {
          headers: {
            Authorization: localStorage.getItem('token')
          }
        }).then((rs) => {
          this.tableData = []
          console.log(rs.data)
          rs.data.forEach(item => { this.tableData.push(item) })
        })
      } else {
        this.selectAllVideos()
      }
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
