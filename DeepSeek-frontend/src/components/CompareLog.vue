<template>
  <div>
    <!-- 信息表格   -->
    <el-table
      :data="tableData"
      border
      style="width: 100%">
      <el-table-column
        prop="videoName"
        label="视频名称"
        min-width=15%>
      </el-table-column>
      <el-table-column
        prop="targetName"
        label="目标视频"
        min-width=15%>
      </el-table-column>
      <el-table-column
        prop="owner"
        label="目标用户"
        min-width=10%>
      </el-table-column>
      <el-table-column
        prop="avgRate"
        label="视频相似度"
        min-width=15%>
      </el-table-column>
      <el-table-column
        prop="txtRate"
        label="文本相似度"
        min-width=15%>
      </el-table-column>
      <el-table-column
        prop="logTime"
        label="时间"
        min-width=20%>
      </el-table-column>
      <el-table-column
        label="操作"
        min-width=10%>
        <template slot-scope="scope">
          <el-button @click="logDownload(scope.row)" type="text" size="small">下 载</el-button>
          <!-- <el-button type="text" size="small" @click="handleDelete(scope.row, scope.$index)">删 除</el-button> -->
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import axios from 'axios'
import baseApiUrl from '../../config.default'

export default {
  name: 'CompareLog',
  data () {
    return {
      fileList: [],
      hashList: [],
      form: {
        title: '',
        description: ''
      },
      loading: false,
      headerObj: {
        Authorization: localStorage.getItem('token')
      },
      tableData: []
    }
  },
  mounted () {
    this.selectMyLog()
  },
  methods: {
    selectMyLog () {
      this.tableData = []
      const url = `${baseApiUrl}/getlog`
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
    logDownload: function (row) {
      const url = `${baseApiUrl}/download` + '?file=' + row.logfile
      axios.get(url, {
        headers: {
          Authorization: localStorage.getItem('token')
        },
        responseType: 'blob'
      }).then(rs => {
        if (rs.status === 200) {
          const blob = new Blob([rs.data])
          const link = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = link
          a.download = row.logfile + '.pdf'
          a.click()
          window.URL.revokeObjectURL(link)
        }
      }).catch(error => {
        this.$message.error('下载失败')
        console.log(error)
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
