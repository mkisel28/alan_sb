<template>
  <div class="p-3 md:p-6 bg-gray-50 min-h-screen">
    <!-- Заголовок -->
    <div class="mb-4 md:mb-6">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Сравнительная аналитика по платформам</h1>
      <p class="text-sm md:text-base text-gray-600">Сравнение всех авторов холдинга по каждой социальной сети с перцентильным скорингом</p>
    </div>

    <!-- Фильтры -->
    <ComparativeFilters
      :selected-platforms="selectedPlatforms"
      :period="period"
      :include-previous="includePrevious"
      :loading="loading"
      @update:platforms="selectedPlatforms = $event"
      @update:period="period = $event"
      @update:includePrevious="includePrevious = $event"
      @load="loadAnalytics"
    />

    <!-- Кнопки экспорта -->
    <div v-if="!loading && analyticsData" class="mb-4 md:mb-6 flex flex-wrap gap-3">
      <el-button
        type="primary"
        :icon="Download"
        @click="downloadWordReport"
        :loading="exportingWord"
      >
        Скачать отчет Word
      </el-button>
      <el-button
        type="success"
        :icon="Download"
        @click="downloadExcelReport"
        :loading="exportingExcel"
      >
        Скачать данные Excel
      </el-button>
    </div>

    <!-- Информация о периоде -->
    <div v-if="analyticsData && analyticsData.period" class="mb-4 md:mb-6">
      <el-alert type="info" :closable="false">
        <template #title>
          <div class="flex flex-col md:flex-row md:justify-between md:items-center gap-2">
            <span class="text-sm md:text-base">
              Период анализа: {{ formatDate(analyticsData.period.start) }} - {{ formatDate(analyticsData.period.end) }}
              ({{ analyticsData.period.days }} дней)
            </span>
            <span v-if="analyticsData.previous_period" class="text-xs md:text-sm text-gray-600">
              Предыдущий период: {{ formatDate(analyticsData.previous_period.start) }} - {{ formatDate(analyticsData.previous_period.end) }}
            </span>
          </div>
        </template>
      </el-alert>
    </div>

    <!-- Блоки по платформам -->
    <div v-if="!loading && analyticsData" class="space-y-6 md:space-y-8">
      <div
        v-for="(platformData, platform) in analyticsData.platforms"
        :key="platform"
        class="platform-block"
      >
        <!-- Заголовок платформы -->
        <div
          class="rounded-t-xl p-4 md:p-6 text-white"
          :class="getPlatformGradient(platform)"
        >
          <div class="flex justify-between items-center">
            <div>
              <h2 class="text-xl md:text-2xl font-bold mb-2">{{ getPlatformName(platform) }}</h2>
              <p class="text-sm md:text-base text-white/90">{{ platformData.aggregated.total_authors }} авторов</p>
            </div>
            <div class="text-right">
              <div class="text-2xl md:text-3xl font-bold">{{ platformData.aggregated.avg_PS }}</div>
              <div class="text-xs md:text-sm text-white/90">Средний PS</div>
              <div v-if="includePrevious && platformData.aggregated.avg_MS !== undefined" class="mt-2">
                <div class="text-xl md:text-2xl font-bold">{{ platformData.aggregated.avg_MS }}</div>
                <div class="text-xs md:text-sm text-white/90">Средний MS</div>
              </div>
            </div>
          </div>

          <!-- Агрегированная статистика -->
          <div class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mt-4">
            <div class="bg-white/20 rounded-lg p-3">
              <div class="text-xl md:text-2xl font-bold">{{ formatNumber(platformData.aggregated.total_followers) }}</div>
              <div class="text-xs md:text-sm text-white/90">Всего подписчиков</div>
            </div>
            <div class="bg-white/20 rounded-lg p-3">
              <div class="text-xl md:text-2xl font-bold">{{ platformData.aggregated.total_posts }}</div>
              <div class="text-xs md:text-sm text-white/90">Всего постов</div>
            </div>
            <div class="bg-white/20 rounded-lg p-3">
              <div class="text-xl md:text-2xl font-bold">{{ formatNumber(platformData.aggregated.total_views) }}</div>
              <div class="text-xs md:text-sm text-white/90">Всего просмотров</div>
            </div>
            <div class="bg-white/20 rounded-lg p-3">
              <div class="text-xl md:text-2xl font-bold">{{ (platformData.aggregated.avg_ER_view * 100).toFixed(2) }}%</div>
              <div class="text-xs md:text-sm text-white/90">Средний ER</div>
            </div>
          </div>
        </div>

        <!-- Сводка по платформе -->
        <div class="bg-white p-4 md:p-6">
          <PlatformSummary :aggregated="platformData.aggregated" />
        </div>

        <!-- Графики сравнения -->
        <div class="bg-white p-4 md:p-6">
          <h3 class="text-lg md:text-xl font-bold mb-4 md:mb-6">Визуализация метрик</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-2 gap-4 md:gap-6 mb-6">
            <!-- Presence Score -->
            <ComparativePresenceScore :authors="platformData.authors" />
            
            <!-- Momentum Score -->
            <ComparativeMomentumScore v-if="includePrevious" :authors="platformData.authors" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-2 gap-4 md:gap-6 mb-6">
            <!-- Просмотры -->
            <ComparativeViewsChart :authors="platformData.authors" />
            
            <!-- Вовлеченность -->
            <ComparativeEngagementChart :authors="platformData.authors" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-2 gap-4 md:gap-6 mb-6">
            <!-- Рост подписчиков -->
            <ComparativeGrowthChart :authors="platformData.authors" />
            
            <!-- Вирусность -->
            <ComparativeViralityChart :authors="platformData.authors" />
          </div>

          <!-- Радар топ-5 авторов -->
          <div class="mb-6">
            <ComparativeRadarChart :authors="platformData.authors" />
          </div>
        </div>

        <!-- Таблица авторов с перцентилями -->
        <el-card class="rounded-t-none">
          <template #header>
            <h3 class="text-lg font-semibold">Детальная таблица авторов</h3>
          </template>
          <el-table
            :data="platformData.authors"
            stripe
            :default-sort="{ prop: 'scores.PS', order: 'descending' }"
            class="w-full"
            :max-height="600"
          >
            <el-table-column prop="author_name" label="Автор" min-width="180" fixed>
              <template #default="{ row }">
                <div>
                  <div class="font-semibold">{{ row.author_name }}</div>
                  <div class="text-sm text-gray-500">@{{ row.username || row.social_account_id }}</div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="Scores" min-width="130">
              <template #default="{ row }">
                <div class="space-y-1">
                  <div class="flex items-center justify-between">
                    <span class="text-xs text-gray-500">PS:</span>
                    <el-tag
                      :type="getScoreType(row.scores.PS)"
                      size="small"
                      class="font-bold"
                    >
                      {{ row.scores.PS }}
                    </el-tag>
                  </div>
                  <div v-if="includePrevious && row.scores.MS !== undefined" class="flex items-center justify-between">
                    <span class="text-xs text-gray-500">MS:</span>
                    <el-tag
                      :type="getScoreType(row.scores.MS)"
                      size="small"
                      class="font-bold"
                    >
                      {{ row.scores.MS }}
                    </el-tag>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="metrics.F" label="Подписчики" min-width="140" sortable>
              <template #default="{ row }">
                <div>
                  <div class="font-semibold">{{ formatNumber(row.metrics.F) }}</div>
                  <div
                    v-if="row.metrics.delta_F !== 0"
                    class="text-xs"
                    :class="row.metrics.delta_F > 0 ? 'text-green-600' : 'text-red-600'"
                  >
                    {{ row.metrics.delta_F > 0 ? '+' : '' }}{{ formatNumber(row.metrics.delta_F) }}
                    ({{ (row.metrics.delta_F_percent * 100).toFixed(1) }}%)
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="metrics.P" label="Посты" min-width="90" sortable align="center" />

            <el-table-column prop="metrics.V_avg" label="V_avg" min-width="130" sortable>
              <template #default="{ row }">
                <div>
                  <div class="font-semibold">{{ formatNumber(row.metrics.V_avg) }}</div>
                  <div class="text-xs text-gray-500">
                    pct: {{ row.scores.percentiles.V_avg }}
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="metrics.E_avg" label="E_avg" min-width="120" sortable>
              <template #default="{ row }">
                {{ formatNumber(row.metrics.E_avg) }}
              </template>
            </el-table-column>

            <el-table-column prop="metrics.ER_view" label="ER_view" min-width="130" sortable>
              <template #default="{ row }">
                <div>
                  <div class="font-semibold">{{ (row.metrics.ER_view * 100).toFixed(2) }}%</div>
                  <div class="text-xs text-gray-500">
                    pct: {{ row.scores.percentiles.ER_view }}
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="metrics.SR" label="SR" min-width="120" sortable>
              <template #default="{ row }">
                <div>
                  <div class="font-semibold">{{ (row.metrics.SR * 100).toFixed(2) }}%</div>
                  <div class="text-xs text-gray-500">
                    pct: {{ row.scores.percentiles.SR }}
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="metrics.CR" label="CR" min-width="110" sortable>
              <template #default="{ row }">
                {{ (row.metrics.CR * 100).toFixed(2) }}%
              </template>
            </el-table-column>

            <el-table-column label="Детали" width="110" fixed="right" align="center">
              <template #default="{ row }">
                <el-button
                  size="small"
                  @click="showAuthorDetails(row)"
                >
                  Подробнее
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>

    <!-- Состояние загрузки -->
    <div v-if="loading" class="text-center py-12">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p class="mt-4 text-gray-600">Загрузка аналитики...</p>
    </div>

    <!-- Пустое состояние -->
    <el-empty
      v-if="!loading && (!analyticsData || Object.keys(analyticsData.platforms || {}).length === 0)"
      description="Выберите платформы и нажмите 'Загрузить аналитику'"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Loading, Download } from '@element-plus/icons-vue'
import api from '../api'
import PlatformSummary from '../components/analytics/comparative/PlatformSummary.vue'
import ComparativeViewsChart from '../components/analytics/comparative/ComparativeViewsChart.vue'
import ComparativeEngagementChart from '../components/analytics/comparative/ComparativeEngagementChart.vue'
import ComparativePresenceScore from '../components/analytics/comparative/ComparativePresenceScore.vue'
import ComparativeMomentumScore from '../components/analytics/comparative/ComparativeMomentumScore.vue'
import ComparativeGrowthChart from '../components/analytics/comparative/ComparativeGrowthChart.vue'
import ComparativeViralityChart from '../components/analytics/comparative/ComparativeViralityChart.vue'
import ComparativeRadarChart from '../components/analytics/comparative/ComparativeRadarChart.vue'
import ComparativeFilters from '../components/analytics/comparative/ComparativeFilters.vue'

const loading = ref(false)
const exportingWord = ref(false)
const exportingExcel = ref(false)
const analyticsData = ref(null)
const selectedPlatforms = ref(['tiktok', 'youtube', 'youtube_shorts', 'instagram'])
const period = ref('30d')
const includePrevious = ref(true)

const loadAnalytics = async () => {
  if (selectedPlatforms.value.length === 0) {
    ElMessage.warning('Выберите хотя бы одну платформу')
    return
  }

  loading.value = true
  try {
    const data = await api.getComparativeAnalytics(
      selectedPlatforms.value,
      period.value,
      null,
      null,
      includePrevious.value
    )
    analyticsData.value = data
    ElMessage.success('Аналитика загружена')
  } catch (error) {
    console.error('Ошибка загрузки аналитики:', error)
    ElMessage.error('Ошибка загрузки аналитики')
  } finally {
    loading.value = false
  }
}

const downloadWordReport = async () => {
  exportingWord.value = true
  try {
    const params = new URLSearchParams()
    selectedPlatforms.value.forEach(p => params.append('platforms', p))
    params.append('period', period.value)
    params.append('include_previous', includePrevious.value)
    
    const response = await fetch(`${api.baseURL}/reports/word?${params}`)
    
    if (!response.ok) {
      throw new Error('Ошибка скачивания отчета')
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `analytics_report_${Date.now()}.docx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('Отчет Word скачан')
  } catch (error) {
    console.error('Ошибка скачивания Word:', error)
    ElMessage.error('Ошибка скачивания отчета Word')
  } finally {
    exportingWord.value = false
  }
}

const downloadExcelReport = async () => {
  exportingExcel.value = true
  try {
    const params = new URLSearchParams()
    selectedPlatforms.value.forEach(p => params.append('platforms', p))
    params.append('period', period.value)
    params.append('include_previous', includePrevious.value)
    
    const response = await fetch(`${api.baseURL}/reports/excel?${params}`)
    
    if (!response.ok) {
      throw new Error('Ошибка скачивания отчета')
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `analytics_data_${Date.now()}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('Данные Excel скачаны')
  } catch (error) {
    console.error('Ошибка скачивания Excel:', error)
    ElMessage.error('Ошибка скачивания Excel')
  } finally {
    exportingExcel.value = false
  }
}

const getPlatformName = (platform) => {
  const names = {
    tiktok: 'TikTok',
    youtube: 'YouTube',
    youtube_shorts: 'YouTube Shorts',
    instagram: 'Instagram',
    facebook: 'Facebook',
    twitter: 'Twitter/X',
    telegram: 'Telegram'
  }
  return names[platform] || platform
}

const getPlatformGradient = (platform) => {
  const gradients = {
    tiktok: 'bg-gradient-to-br from-pink-500 to-purple-600',
    youtube: 'bg-gradient-to-br from-red-500 to-red-700',
    youtube_shorts: 'bg-gradient-to-br from-red-600 to-pink-600',
    instagram: 'bg-gradient-to-br from-purple-500 to-pink-600',
    facebook: 'bg-gradient-to-br from-blue-500 to-blue-700',
    twitter: 'bg-gradient-to-br from-sky-400 to-blue-500',
    telegram: 'bg-gradient-to-br from-blue-400 to-blue-600'
  }
  return gradients[platform] || 'bg-gradient-to-br from-gray-500 to-gray-700'
}

const getScoreType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'primary'
  if (score >= 40) return 'warning'
  return 'danger'
}

const formatNumber = (num) => {
  if (num === undefined || num === null) return '0'
  return Math.round(num).toLocaleString('ru-RU')
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const showAuthorDetails = (row) => {
  // TODO: Открыть модальное окно с детальной информацией
  console.log('Show details for:', row)
  ElMessage.info('Функция в разработке')
}

// Автозагрузка при монтировании
onMounted(() => {
  loadAnalytics()
})
</script>

<style scoped>
.platform-block {
  @apply shadow-lg rounded-xl overflow-hidden;
}

.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
