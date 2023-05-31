<template>
  <div class="registerbody">
    <div class="registerdata">
      <div class="registertext">
        <h2>注册</h2>
      </div>
      <div class="formdata">
        <el-form ref="form" :model="registerForm" :rules="rules">
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.userName"
              clearable
              placeholder="用户名"
              prefix-icon="el-icon-user"
            ></el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              clearable
              placeholder="密码"
              show-password
              prefix-icon="el-icon-key"
            ></el-input>
          </el-form-item>
          <el-form-item prop="type">
            <div>
              <el-radio v-model="registerForm.type" label="1" border>企业用户</el-radio>
              <el-radio v-model="registerForm.type" label="0" border>个人用户</el-radio>
            </div>
          </el-form-item>
        </el-form>
      </div>
      <div class="butt">
        <el-button type="primary" @click="register"
          >注册</el-button
        >
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import baseApiUrl from '../../config.default'
export default {
  name: 'RegisterPage',
  data () {
    // let vm = this;
    return {
      registerForm: {
        userName: '',
        password: '',
        type: Number
      }
    }
  },
  methods: {
    register () {
      if (this.registerForm.userName && this.registerForm.password) {
        console.log(this.registerForm.type)
        const url = `${baseApiUrl}/register`
        const sha256 = require('js-sha256')
        let formData = 'username=' + this.registerForm.userName
        formData = formData.concat('&password=' + sha256(this.registerForm.password))
        formData = formData.concat('&type=' + this.registerForm.type)
        axios.post(url, formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
          }
        }).then(response => {
          console.log('注册信息:', response)
          if (response.status === 200) {
            this.$message.success('注册成功')
            localStorage.setItem('token', response.data.token)
            this.$router.push('/')
          }
        }).catch(() => {
          this.$message.error('注册失败')
        })
      } else if (!this.registerForm.userName) {
        this.$message.error('用户名不能为空')
      } else if (!this.registerForm.password) {
        this.$message.error('密码不能为空')
      }
    }
  }
}
</script>

<style>
body {
  margin: 0;
}
.registerbody {
  width: 100%;
  height: 100%;
  min-width: 1000px;
  background-image: url("../assets/bupt3.jpg");
  background-size: 100% 100%;
  background-position: center center;
  overflow: auto;
  background-repeat: no-repeat;
  position: fixed;
  line-height: 100%;
  padding-top: 150px;
}

.registertext {
  margin-bottom: 20px;
  line-height: 50px;
  text-align: center;
  font-size: 30px;
  font-weight: bolder;
  color: white;
  text-shadow: 2px 2px 4px #000000;
}

.registerdata {
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
  display: flex;
  justify-content: space-between;
  color: #606266;
}

.butt {
  margin-top: 10px;
  text-align: center;
}

.shou {
  cursor: pointer;
  color: #606266;
}
</style>
