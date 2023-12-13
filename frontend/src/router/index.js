import { createRouter, createWebHistory } from 'vue-router'
import AppliancesDashboardView from '../views/AppliancesDashboardView.vue'
import HomeDashboardView from '../views/HomeDashboardView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/',
      alias: '/home',
      name: 'home-dashboard',
      component: () => import('../views/HomeDashboardView.vue')
    },
    {
      path: '/energy',
      name: 'energy-dashboard',
      component: () => import('../views/EnergyDashboardView.vue')
    },
    {
      path: '/heating',
      name: 'heating-dashboard',
      component: () => import('../views/HeatingDashboardView.vue')
    },
    {
      path: '/charts',
      name: 'charts-dashboard',
      component: () => import('../views/ChartsDashboardView.vue')
    },
    {
      path: '/appliances',
      name: 'appliances-dashboard',
      component: () => import('../views/AppliancesDashboardView.vue')
    },
  ]
})

export default router
