<template>
  <div class="home-page">
    <!-- Stats Overview -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-icon">
          <el-icon :size="40" color="#409eff"><User /></el-icon>
        </div>
        <div class="stat-value">{{ stats.totalAuthors }}</div>
        <div class="stat-label">Всего авторов</div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-icon">
          <el-icon :size="40" color="#67c23a"><Connection /></el-icon>
        </div>
        <div class="stat-value">{{ stats.totalAccounts }}</div>
        <div class="stat-label">Подключенных аккаунтов</div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-icon">
          <el-icon :size="40" color="#e6a23c"><VideoPlay /></el-icon>
        </div>
        <div class="stat-value">{{ stats.totalVideos }}</div>
        <div class="stat-label">Собрано видео</div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-icon">
          <el-icon :size="40" color="#f56c6c"><View /></el-icon>
        </div>
        <div class="stat-value">{{ formatNumber(stats.totalViews) }}</div>
        <div class="stat-label">Всего просмотров</div>
      </el-card>
    </div>

    <!-- Quick Actions -->
    <el-card class="quick-actions">
      <template #header>
        <div class="card-header">
          <span>Быстрые действия</span>
        </div>
      </template>

      <div class="actions-grid">
        <el-button type="primary" size="large" @click="$router.push('/authors')">
          <el-icon><Plus /></el-icon>
          Добавить автора
        </el-button>

        <el-button type="success" size="large" @click="showCollectDialog = true">
          <el-icon><Download /></el-icon>
          Собрать данные
        </el-button>

        <el-button type="warning" size="large" @click="$router.push('/comparative-analytics')">
          <el-icon><DataAnalysis /></el-icon>
          Сравнительная аналитика
        </el-button>
      </div>
    </el-card>

    <!-- Recent Activity -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Последняя активность</span>
          <el-button text @click="loadStats">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </template>

      <el-empty v-if="!recentAuthors.length" description="Нет данных" />
      
      <div v-else class="recent-list">
        <div
          v-for="author in recentAuthors"
          :key="author.id"
          class="recent-item"
          @click="$router.push(`/authors/${author.id}`)"
        >
          <el-avatar :size="40">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="recent-info">
            <div class="recent-name">{{ author.name }}</div>
            <div class="recent-date">{{ formatDate(author.created_at) }}</div>
          </div>
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </el-card>

    <!-- Collect Data Dialog -->
    <el-dialog
      v-model="showCollectDialog"
      title="Массовый сбор данных"
      width="600px"
    >
      <el-form :model="collectForm" label-width="150px">
        <el-form-item label="Режим сбора">
          <el-radio-group v-model="collectForm.mode">
            <el-radio label="all">Все аккаунты всех авторов</el-radio>
            <el-radio label="selected">Выборочно</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="collectForm.mode === 'selected'" label="Авторы">
          <el-select 
            v-model="collectForm.selectedAuthors" 
            placeholder="Выберите авторов"
            multiple
            collapse-tags
            collapse-tags-tooltip
            style="width: 100%"
          >
            <el-option
              v-for="author in authors"
              :key="author.id"
              :label="`${author.name} (${getAccountsCount(author.id)} аккаунтов)`"
              :value="author.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Макс. видео">
          <el-input-number 
            v-model="collectForm.maxVideos" 
            :min="10" 
            :max="500"
            style="width: 100%"
          />
          <div class="form-hint">Количество видео для сбора с каждого аккаунта</div>
        </el-form-item>

        <el-alert
          v-if="collectForm.mode === 'all'"
          title="Внимание"
          type="warning"
          :closable="false"
          show-icon
        >
          Будет запущен сбор данных для {{ totalAccountsCount }} аккаунтов.
          Запросы выполняются последовательно.
        </el-alert>

        <el-alert
          v-else-if="collectForm.selectedAuthors.length > 0"
          :title="`Будет обработано аккаунтов: ${selectedAccountsCount}`"
          type="info"
          :closable="false"
          show-icon
        />
      </el-form>

      <template #footer>
        <el-button @click="showCollectDialog = false">Отмена</el-button>
        <el-button 
          type="primary" 
          @click="handleMassCollect" 
          :loading="collecting"
          :disabled="collectForm.mode === 'selected' && collectForm.selectedAuthors.length === 0"
        >
          Начать сбор
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthorsStore } from '@/stores/authors'
import { useSocialAccountsStore } from '@/stores/socialAccounts'
import { useCollectionProgressStore } from '@/stores/collectionProgress'
import api from '@/api'
import dayjs from 'dayjs'

const authorsStore = useAuthorsStore()
const socialAccountsStore = useSocialAccountsStore()
const progressStore = useCollectionProgressStore()

const showCollectDialog = ref(false)
const collecting = ref(false)
const collectForm = ref({
  mode: 'all',
  selectedAuthors: [],
  maxVideos: 100
})

const accountsCounts = ref({})

const stats = ref({
  totalAuthors: 0,
  totalAccounts: 0,
  totalVideos: 0,
  totalViews: 0
})

const authors = computed(() => authorsStore.authors)
const recentAuthors = computed(() => 
  authorsStore.authors.slice(0, 5)
)

const totalAccountsCount = computed(() => {
  return Object.values(accountsCounts.value).reduce((sum, count) => sum + count, 0)
})

const selectedAccountsCount = computed(() => {
  return collectForm.value.selectedAuthors.reduce((sum, authorId) => {
    return sum + (accountsCounts.value[authorId] || 0)
  }, 0)
})

const getAccountsCount = (authorId) => {
  return accountsCounts.value[authorId] || 0
}

const loadAccountsCounts = async () => {
  for (const author of authorsStore.authors) {
    const accounts = await api.getSocialAccounts(author.id)
    accountsCounts.value[author.id] = accounts.length
  }
}

const loadStats = async () => {
  await authorsStore.fetchAuthors()
  await loadAccountsCounts()
  
  stats.value.totalAuthors = authorsStore.authors.length
  stats.value.totalAccounts = totalAccountsCount.value
  
  // Simplified stats calculation
  let videosCount = 0
  let viewsCount = 0
  
  for (const author of authorsStore.authors) {
    const accounts = await api.getSocialAccounts(author.id)
    
    for (const account of accounts) {
      const videos = await api.getVideos(account.id)
      videosCount += videos.length
      viewsCount += videos.reduce((sum, v) => sum + (v.views_count || 0), 0)
    }
  }
  
  stats.value.totalVideos = videosCount
  stats.value.totalViews = viewsCount
}

const handleMassCollect = async () => {
  let accountsToCollect = []
  
  // Определяем список аккаунтов для сбора
  if (collectForm.value.mode === 'all') {
    // Собираем все аккаунты всех авторов
    for (const author of authorsStore.authors) {
      const accounts = await api.getSocialAccounts(author.id)
      accountsToCollect.push(...accounts.map(acc => ({
        ...acc,
        authorName: author.name
      })))
    }
  } else {
    // Собираем аккаунты выбранных авторов
    for (const authorId of collectForm.value.selectedAuthors) {
      const author = authorsStore.authors.find(a => a.id === authorId)
      const accounts = await api.getSocialAccounts(authorId)
      accountsToCollect.push(...accounts.map(acc => ({
        ...acc,
        authorName: author.name
      })))
    }
  }

  if (accountsToCollect.length === 0) {
    ElMessage.warning('Нет аккаунтов для сбора данных')
    return
  }

  showCollectDialog.value = false
  progressStore.startCollection(accountsToCollect.length)

  // Последовательная обработка каждого аккаунта
  for (const account of accountsToCollect) {
    const accountLabel = `${account.authorName} - @${account.username || account.platform_user_id}`
    progressStore.updateProgress(accountLabel)

    try {
      // Выбираем правильный endpoint в зависимости от платформы
      if (account.platform === 'tiktok') {
        await api.collectTikTokData(account.id, collectForm.value.maxVideos)
      } else if (account.platform === 'youtube' || account.platform === 'youtube_shorts') {
        await api.collectYouTubeData(account.id, collectForm.value.maxVideos)
      } else {
        throw new Error(`Платформа ${account.platform} пока не поддерживается`)
      }
      progressStore.markCompleted()
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || 'Неизвестная ошибка'
      progressStore.markFailed(accountLabel, errorMsg)
    }

    // Небольшая задержка между запросами
    await new Promise(resolve => setTimeout(resolve, 500))
  }

  progressStore.finishCollection()
  
  // Обновляем статистику после сбора
  await loadStats()

  ElMessage.success(`Сбор завершен! Обработано: ${accountsToCollect.length}`)
}

const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num
}

const formatDate = (date) => {
  return dayjs(date).format('DD.MM.YYYY HH:mm')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home-page {
  max-width: 1400px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-icon {
  margin-bottom: 12px;
}

.stat-value {
  font-size: 36px;
  font-weight: 600;
  margin: 8px 0;
  color: #303133;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.quick-actions {
  margin-bottom: 24px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.recent-item:hover {
  background: #f5f7fa;
}

.recent-info {
  flex: 1;
}

.recent-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.recent-date {
  font-size: 12px;
  color: #909399;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
