<template>
  <el-config-provider :locale="locale">
    <div class="app-container">
      <!-- Global Collection Progress Toast -->
      <CollectionProgressToast />
      
      <el-container>
        <!-- Sidebar -->
        <el-aside width="250px" class="sidebar">
          <div class="logo">
            <el-icon :size="32"><TrendCharts /></el-icon>
            <h2>Analytics</h2>
          </div>
          
          <el-menu
            :default-active="currentRoute"
            router
            class="sidebar-menu"
            background-color="#001529"
            text-color="#ffffff"
            active-text-color="#ffd666"
          >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>Главная</span>
          </el-menu-item>

          <el-menu-item index="/authors">
            <el-icon><User /></el-icon>
            <span>Авторы</span>
          </el-menu-item>

          <el-menu-item index="/telegram-analytics">
            <el-icon><ChatDotRound /></el-icon>
            <span>Telegram Аналитика</span>
          </el-menu-item>

          <el-menu-item index="/analytics">
            <el-icon><DataAnalysis /></el-icon>
            <span>Аналитика</span>
          </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- Main Content -->
        <el-container>
          <el-header class="header">
            <div class="header-content">
              <h1>{{ pageTitle }}</h1>
              <div class="header-actions">
                <el-button @click="refreshData" circle>
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </div>
            </div>
          </el-header>

          <el-main class="main-content">
            <router-view v-slot="{ Component }">
              <transition name="fade" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </el-main>
        </el-container>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ruRU from 'element-plus/dist/locale/ru.mjs'
import CollectionProgressToast from '@/components/CollectionProgressToast.vue'

const route = useRoute()
const locale = ruRU

const currentRoute = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/': 'Панель управления',
    '/authors': 'Управление авторами',
    '/analytics': 'Аналитика'
  }
  return titles[route.path] || 'Analytics'
})

const refreshData = () => {
  window.location.reload()
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.sidebar {
  background: #001529;
  color: white;
  min-height: 100vh;
  overflow-y: auto;
  position: sticky;
  top: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
}

.header {
  background: white;
  border-bottom: 1px solid #e8e8e8;
  padding: 0 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.main-content {
  background: #f5f5f5;
  padding: 24px;
  flex: 1;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Глобальные стили для контейнеров */
.el-container {
  min-height: 100vh;
}

.el-main {
  overflow: visible !important;
}
</style>
