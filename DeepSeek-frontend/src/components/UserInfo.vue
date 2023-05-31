<template>
  <div>
    <el-card>
      <el-descriptions class="margin-top" title="个人信息" :column="1" border>
        <el-descriptions-item>
          <template slot="label">
            <i class="el-icon-picture-outline"></i>
            头像
          </template>
          <el-upload
            class="avatar-uploader"
            :action="uploadUrl"
            :headers="headerObj"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload">
            <img v-if="avatar" :src="avatar" class="img">
            <i v-else class="avatar-uploader-icon">点击修改头像</i>
          </el-upload>
        </el-descriptions-item>
        <el-descriptions-item>
          <template slot="label">
            <i class="el-icon-user"></i>
            用户名
          </template>
          {{ username }}
        </el-descriptions-item>
        <el-descriptions-item>
          <template slot="label">
            <i class="el-icon-info"></i>
            用户类型
          </template>
          {{ type }}
        </el-descriptions-item>
        <el-descriptions-item>
          <template slot="label">
            <i class="el-icon-odometer"></i>
            剩余使用次数
          </template>
          {{ remains }}
        </el-descriptions-item>
        <el-descriptions-item>
          <template slot="label">
            <i class="el-icon-shopping-cart-2"></i>
            充值
          </template>
          <span><el-button @click="charge(50)" type="success" size="medium" round>50</el-button></span>
          <span>{{ '\u3000' }}</span>
          <span><el-button @click="charge(100)" type="success" size="medium" round>100</el-button></span>
          <span>{{ '\u3000' }}</span>
          <span><el-button @click="charge(150)" type="success" size="medium" round>150</el-button></span>
          <span>{{ '\u3000' }}</span>
          <span><el-button @click="charge(200)" type="success" size="medium" round>200</el-button></span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
import baseApiUrl from '../../config.default'

export default {
  name: 'UserInfo',
  data () {
    return {
      username: String,
      avatar: String,
      type: String,
      remains: Number,
      uploadUrl: baseApiUrl + '/avatar',
      headerObj: {
        Authorization: localStorage.getItem('token')
      }
    }
  },
  mounted () {
    this.load()
  },
  methods: {
    load () {
      const url = `${baseApiUrl}/getinfo`
      axios.get(url, {
        headers: {
          Authorization: localStorage.getItem('token')
        }
      }).then(rs => {
        this.username = rs.data.username
        localStorage.setItem('avatar', rs.data.avatar)
        if (rs.data.avatar === 'default_avatar') {
          this.avatar = require('../assets/default_avatar.jpg')
        } else {
          this.avatar = require('../../public/avatar/' + rs.data.avatar)
        }
        this.remains = rs.data.remains
        if (rs.data.type) {
          this.type = '企业用户'
        } else {
          this.type = '个人用户'
        }
      }).catch((err) => {
        console.log(err)
      })
    },
    charge (num) {
      const url = `${baseApiUrl}/charge?num=` + num
      axios.get(url, {
        headers: {
          Authorization: localStorage.getItem('token')
        }
      }).then(rs => {
        this.$message.success('充值成功！')
        this.load()
      }).catch((err) => {
        console.log(err)
      })
    },
    beforeAvatarUpload (file) {
      console.log(file.type)
      const isJPG = file.type === 'image/jpeg'
      const isPNG = file.type === 'image/png'
      const isLt2M = file.size / 1024 / 1024 < 2

      if (!(isJPG || isPNG)) {
        this.$message.error('上传头像图片只能是 JPG 格式!')
      }
      if (!isLt2M) {
        this.$message.error('上传头像图片大小不能超过 2MB!')
      }
      return (isPNG || isJPG) && isLt2M
    },
    handleAvatarSuccess (res, file) {
      this.$message.success('修改头像成功')
      this.load()
    }
  }
}
</script>

<style scoped>
.img {
  width: 200px;
  height: 200px;
}
</style>
