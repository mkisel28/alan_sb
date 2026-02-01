import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue')
  },
  {
    path: '/authors',
    name: 'Authors',
    component: () => import('@/views/AuthorsPage.vue')
  },
  {
    path: '/authors/:id',
    name: 'AuthorSocialAccounts',
    component: () => import('@/views/AuthorSocialAccountsPage.vue')
  },
  {
    path: '/authors/:id/social/:socialId',
    name: 'SocialAccountDetail',
    component: () => import('@/views/SocialAccountDetailPage.vue')
  },
  {
    path: '/authors/:id/social/:socialId/analytics',
    name: 'Analytics',
    component: () => import('@/views/AnalyticsPage.vue')
  },
  {
    path: '/comparative-analytics',
    name: 'ComparativeAnalytics',
    component: () => import('@/views/ComparativeAnalyticsPage.vue')
  },
  {
    path: '/telegram-analytics',
    name: 'TelegramAnalytics',
    component: () => import('@/views/TelegramAnalyticsPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
