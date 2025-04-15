import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from "@/views/LoginView.vue";
import RegisterView from "@/views/RegisterView.vue";
import DeviceList from '../components/DeviceList.vue'
import DeviceDetail from '../components/DeviceDetails.vue'
import CommandHistory from '../components/CommandHistory.vue'
import TokenGenerator from '../components/TokenGenerator.vue'



const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: DeviceList,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/devices/:deviceId',
      name: 'device-detail',
      component: DeviceDetail,
      props: true
    },
    {
      path: '/commands',
      name: 'commands',
      component: CommandHistory
    },
    {
      path: '/tokens',
      name: 'tokens',
      component: TokenGenerator
    },
  ],
})

export default router