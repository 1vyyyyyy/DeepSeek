<template>
  <el-container style="height: 100%">
    <!--  头部  -->
    <el-header style="background-color: #fffdfd">
      <el-row :gutter="20" justify="space-between">
        <el-col :span="6" style="display: flex; align-items: center; justify-content: space-between;">
          <img alt="" src="../assets/kou2.png" height="60">
          <h3 style="font-weight: 400; font-family: 'STSong'; font-size: 20.5px; vertical-align:middle;">谛视 DeepSeek 管理系统</h3>
        </el-col>
        <el-col :span="16" style="display: flex; justify-content: flex-end; font-family: 'STSong';">
          <el-dropdown>
            <span class="more el-dropdown-link" ref="echarType">
              <div class="mycontainer">
                <img alt="../assets/default_avatar.jpg" :src="avatar" style="vertical-align:middle;display: inline;float: left;height: 55px;border-radius: 50%">
                <span>{{ '\xa0' }}</span>
                <span>{{ username }}</span>
              </div>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item @click.native="jmp2info()">个人中心</el-dropdown-item>
              <el-dropdown-item @click.native="logOut()">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </el-col>
      </el-row>
    </el-header>
    <el-container>
      <!--  侧边栏   -->
      <el-aside width="200px" style="background-color: #E6F3F9">
        <el-menu class="el-menu-demo" style="background-color: #E6F3F9; margin-top: 15px" :default-active="this.$route.path" router>
          <el-menu-item index="/home/videoManagement" style="font-size: 16px;vertical-align:middle;font-family: 'STSong';"><i class="el-icon-monitor" style="margin-right: 16px"></i>视频管理</el-menu-item>
          <el-menu-item index="/home/videoInfo" style="font-size: 16px;vertical-align:middle;font-family: 'STSong';"><i class="el-icon-cloudy" style="margin-right: 16px"></i>视频总览</el-menu-item>
          <el-menu-item index="/home/compareLog" style="font-size: 16px;vertical-align:middle;font-family: 'STSong';"><i class="el-icon-document" style="margin-right: 16px"></i>我的日志</el-menu-item>
        </el-menu>
      </el-aside>
      <!--   主题区域   -->
      <el-main style="background-color: rgb(246, 246, 246)">
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import axios from 'axios'
import baseApiUrl from '../../config.default'

export default {
  name: 'Home',
  data () {
    return {
      username: localStorage.getItem('username'),
      avatar: localStorage.getItem('avatar')
    }
  },
  mounted () {
    this.setAvatar()
  },
  methods: {
    setAvatar () {
      if (this.avatar === 'default_avatar') {
        this.avatar = require('../assets/default_avatar.jpg')
      } else {
        this.avatar = require('../../public/avatar/' + this.avatar)
      }
    },
    logOut () {
      this.$confirm('是否确定退出登录？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const url = `${baseApiUrl}/logout`
        axios.get(url, {
          headers: {
            Authorization: localStorage.getItem('token')
          }
        }).then(rs => {
          if (rs.status === 200) {
            localStorage.removeItem('token')
            this.$router.push('/')
          }
        }).catch(error => {
          if (error.response.status === 401) {
            this.$message.error('退出失败')
          }
        })
      })
    },
    jmp2info () {
      this.$router.push('/home/userInfo')
    }
  }
}
</script>

<style>

.more {
  margin-top: 4px;
  font-size: 21px;
  vertical-align: middle
}

.mycontainer {
  display: flex;
  align-items: center;
}
</style>
