<template>
  <div class="loginbody">
    <div class="logindata">
      <div class="logintext">
        <h2>登录</h2>
      </div>
      <div class="formdata">
        <el-form ref="form" :model="loginForm" :rules="rules">
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.userName"
              clearable
              placeholder="用户名"
              prefix-icon="el-icon-user"
            ></el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              clearable
              placeholder="密码"
              show-password
              prefix-icon="el-icon-key"
            ></el-input>
          </el-form-item>
        </el-form>
        <div>
          <el-checkbox v-model="checked" @change="remember">记住密码</el-checkbox>
        </div>
      </div>
      <div class="butt">
        <el-button type="primary" @click="login">登录</el-button>
        <el-button class="shou" @click="jmp2register">注册</el-button>
      </div>
      <div class="tool">
        <div>
          <span class="forg" @click="forgetpass">忘记密码？</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import baseApiUrl from '../../config.default'

export default {
  name: 'LoginPage',
  data () {
    // let vm = this;
    return {
      loginForm: {
        userName: '',
        password: ''
      },
      checked: false,
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    login () {
      if (this.loginForm.userName && this.loginForm.password) {
        const url = `${baseApiUrl}/login`
        let formData = 'username=' + this.loginForm.userName
        const sha256 = require('js-sha256')
        formData = formData.concat('&password=' + sha256(this.loginForm.password))
        axios.post(url, formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
          }
        }).then(response => {
          // console.log('登录信息:', response.data.token)
          if (response.status === 200) {
            this.$message.success('登录成功')
            localStorage.setItem('username', this.loginForm.userName)
            localStorage.setItem('token', response.data.token)
            localStorage.setItem('avatar', response.data.avatar)
            this.$router.push('/home')
          } else if (response.status === 402) {
            this.$message.error('请检查用户名和密码')
          }
        }).catch(() => {
          this.$message.error('登录失败，请检查用户名和密码')
        })
      } else if (!this.loginForm.userName) {
        this.$message.error('请输入用户名')
      } else if (!this.loginForm.password) {
        this.$message.error('请输入密码')
      }
    },
    jmp2register () {
      this.$router.push('/register')
    },
    remember (data) {
      this.checked = data
      if (this.checked) {
        localStorage.setItem('news', JSON.stringify(this.form))
      } else {
        localStorage.removeItem('news')
      }
    },
    forgetpass () {
      this.$message({
        type: 'info',
        message: '该功能尚未开发捏😥',
        showClose: true
      })
    }
  }
}
</script>

<style>
body {
  margin: 0;
}
.loginbody {
  width: 100%;
  height: 100%;
  min-width: 1000px;
  background-image: url("../assets/bupt2.jpg");
  background-size: 100% 100%;
  background-position: center center;
  overflow: auto;
  background-repeat: no-repeat;
  position: fixed;
  line-height: 100%;
  padding-top: 150px;
}

.logintext {
  line-height: 20px;
  text-align: center;
  font-size: 30px;
  font-weight: bolder;
  color: white;
  text-shadow: 2px 2px 4px #000000;
}

.logindata {
  width: 450px;
  height: 400px;
  transform: translate(-50%);
  margin-left: 50%;
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.tool {
  /* display: flex;
  justify-content: space-between;
  color: #606266; */
  position: absolute;
  right: 2px;
  bottom: 30px;
}

.butt {
  text-align: center;
}

.shou {
  cursor: pointer;
  color: #606266;
}

.forg {
  cursor: pointer;
  text-decoration: underline;
  font-family:Arial, Helvetica, sans-serif;
  font-weight: 50;
  font-size: 90%;
}
</style>
