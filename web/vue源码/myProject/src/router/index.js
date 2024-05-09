import Vue from 'vue'
import Router from 'vue-router'
import SearchImg from '@/components/SearchImg'
import SearchFace from '@/components/SearchFace'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'SearchImg',
      component: SearchImg
    },
    {
      path: '/SearchImg',
      name: 'SearchImg',
      component: SearchImg
    },
    {
      path: '/searchFace',
      name: 'SearchFace',
      component: SearchFace
    }
  ]
})
