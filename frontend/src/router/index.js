import { createRouter, createWebHistory } from 'vue-router'
import AppliancesDashboardView from '../views/AppliancesDashboardView.vue'
import HomeDashboardView from '../views/HomeDashboardView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      alias: '/home',
      name: 'home-dashboard',
      component: () => import('../views/HomeDashboardView.vue')
    },
    {
      path: '/heating',
      name: 'heating-dashboard',
      component: () => import('../views/HeatingDashboardView.vue')
    },
    {
      path: '/appliances',
      name: 'appliances-dashboard',
      component: () => import('../views/AppliancesDashboardView.vue')
    },
  ]
})

export default router
