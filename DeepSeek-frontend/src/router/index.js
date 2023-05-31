import Vue from 'vue'
import VueRouter from 'vue-router'
import VideoManagement from '../components/VideoManagement'
import VideoInfo from '../components/VideoInfo'
import UserInfo from '../components/UserInfo'
import CompareLog from '../components/CompareLog'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'login',
    component: () => import('../views/Login')
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/Register')
  },
  {
    path: '/home',
    name: 'home',
    redirect: '/home/videoManagement',
    component: () => import('../views/Home'),
    meta: { isAuth: true, title: '主页' },
    children: [
      {
        path: '/home/videoManagement',
        name: 'videoManagement',
        component: VideoManagement,
        meta: { isAuth: true, title: '视频管理' }
      },
      {
        path: '/home/videoInfo',
        name: 'videoInfo',
        component: VideoInfo,
        meta: { isAuth: true, title: '视频总览' }
      },
      {
        path: '/home/compareLog',
        name: 'compareLog',
        component: CompareLog,
        meta: { isAuth: true, title: '我的日志' }
      },
      {
        path: '/home/userInfo',
        name: 'userInfo',
        component: UserInfo,
        meta: { isAuth: true, title: '个人中心' }
      }
    ]
  }
]

const router = new VueRouter({
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.isAuth) {
    if (localStorage.getItem('token')) {
      return next()
    } else {
      return next('/')
    }
  } else {
    return next()
  }
})

export default router
