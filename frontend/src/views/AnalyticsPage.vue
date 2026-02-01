<template>
  <div class="analytics-page">
    <div class="header mb-6">
      <h2 class="text-2xl font-bold">Аналитика</h2>
      <div v-if="socialAccount" class="text-gray-600 mt-1">
        {{ socialAccount.platform }} - @{{ socialAccount.username }}
      </div>
    </div>

    <PeriodFilters :loading="loading" @update="handlePeriodUpdate" />

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      class="mt-4"
      show-icon
      closable
    />

    <div v-loading="loading" class="analytics-content">
      <template v-if="analyticsData">
        <!-- Основные метрики -->
        <div class="mb-8">
          <h3 class="text-lg font-semibold mb-4">Основные показатели</h3>
          <MetricsOverview :data="analyticsData" />
          <div class="metrics-description">
            <strong>Расчет:</strong> F - подписчики на конец периода | ΔF = F(конец) - F(начало) | 
            V_avg = Σ(просмотры) / P | E = Σ(лайки + комментарии + шеры + сохранения) | 
            ER_view = (E / V) × 100%
          </div>
        </div>

        <!-- Графики в сетке -->
        <div class="mb-6">
          <h3 class="text-lg font-semibold mb-4">Визуализация данных</h3>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="chart-wrapper">
              <ViewsChart :data="analyticsData" />
              <div class="chart-description">
                <strong>Формула:</strong> V = Σ просмотров | V_avg = V / P | V_median = медиана
              </div>
              <el-button 
                size="small" 
                :icon="FullScreen" 
                circle
                class="expand-btn"
                title="Развернуть на весь экран"
                @click="expandChart('views')"
              />
            </div>

            <div class="chart-wrapper">
              <EngagementChart :data="analyticsData" />
              <div class="chart-description">
                <strong>Формула:</strong> ER_view = (E / V) × 100% | ER_fol = (E / F) × 100%
              </div>
              <el-button 
                size="small" 
                :icon="FullScreen" 
                circle
                class="expand-btn"
                title="Развернуть на весь экран"
                @click="expandChart('engagement')"
              />
            </div>

            <div class="chart-wrapper">
              <ViralityChart :data="analyticsData" />
              <div class="chart-description">
                <strong>Формула:</strong> SR = (шеры / V) × 100% | CR = (комментарии / V) × 100%
              </div>
              <el-button 
                size="small" 
                :icon="FullScreen" 
                circle
                class="expand-btn"
                title="Развернуть на весь экран"
                @click="expandChart('virality')"
              />
            </div>

            <div v-if="analyticsData.comparison" class="chart-wrapper">
              <GrowthChart :data="analyticsData" />
              <div class="chart-description">
                <strong>Формула:</strong> Δ% = ((текущее - предыдущее) / предыдущее) × 100%
              </div>
              <el-button 
                size="small" 
                :icon="FullScreen" 
                circle
                class="expand-btn"
                title="Развернуть на весь экран"
                @click="expandChart('growth')"
              />
            </div>
          </div>
        </div>

        <!-- Детальные метрики -->
        <div>
          <h3 class="text-lg font-semibold mb-4">Подробная статистика</h3>
          <DetailedMetrics :data="analyticsData" />
          <div class="metrics-description">
            <strong>Обозначения:</strong> F - подписчики | P - публикации | V - просмотры | 
            E - вовлеченность | SR - share rate | CR - comment rate
          </div>
        </div>
      </template>

      <el-empty v-else-if="!loading" description="Выберите период для отображения аналитики" />
    </div>

    <!-- Модальное окно для развернутого графика -->
    <el-dialog 
      v-model="expandedChartDialog" 
      :title="expandedChartTitle"
      width="90%"
      :fullscreen="true"
      destroy-on-close
    >
      <div class="expanded-chart-container">
        <ViewsChart v-if="expandedChart === 'views'" :data="analyticsData" />
        <EngagementChart v-if="expandedChart === 'engagement'" :data="analyticsData" />
        <ViralityChart v-if="expandedChart === 'virality'" :data="analyticsData" />
        <GrowthChart v-if="expandedChart === 'growth'" :data="analyticsData" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { FullScreen } from '@element-plus/icons-vue'
import api from '@/api'
import PeriodFilters from '@/components/analytics/PeriodFilters.vue'
import MetricsOverview from '@/components/analytics/MetricsOverview.vue'
import ViewsChart from '@/components/analytics/ViewsChart.vue'
import EngagementChart from '@/components/analytics/EngagementChart.vue'
import ViralityChart from '@/components/analytics/ViralityChart.vue'
import GrowthChart from '@/components/analytics/GrowthChart.vue'
import DetailedMetrics from '@/components/analytics/DetailedMetrics.vue'

const route = useRoute()

const socialAccount = ref(null)
const analyticsData = ref(null)
const loading = ref(false)
const error = ref(null)
const expandedChartDialog = ref(false)
const expandedChart = ref(null)
const expandedChartTitle = ref('')

const chartTitles = {
  views: 'Просмотры',
  engagement: 'Вовлеченность',
  virality: 'Виральность контента',
  growth: 'Рост показателей'
}

const expandChart = (chartType) => {
  expandedChart.value = chartType
  expandedChartTitle.value = chartTitles[chartType]
  expandedChartDialog.value = true
}

const loadSocialAccount = async () => {
  try {
    const accounts = await api.getSocialAccounts(route.params.id)
    socialAccount.value = accounts.find(acc => acc.id === parseInt(route.params.socialId))
  } catch (err) {
    console.error('Failed to load social account:', err)
  }
}

const handlePeriodUpdate = async (periods) => {
  if (!periods || !periods.current) {
    error.value = 'Неверно указаны периоды'
    return
  }

  loading.value = true
  error.value = null

  try {
    const params = {
      current_start: periods.current.start,
      current_end: periods.current.end
    }

    if (periods.previous) {
      params.previous_start = periods.previous.start
      params.previous_end = periods.previous.end
    }

    analyticsData.value = await api.getAnalytics(route.params.socialId, params)
  } catch (err) {
    console.error('Failed to load analytics:', err)
    error.value = err.response?.data?.detail || 'Не удалось загрузить данные аналитики'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSocialAccount()
})
</script>

<style scoped>
.analytics-page {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

.analytics-content {
  min-height: 400px;
}

.chart-wrapper {
  position: relative;
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 520px;
  display: flex;
  flex-direction: column;
}

.chart-wrapper > *:first-child {
  flex: 1;
  min-height: 0;
  max-height: 450px;
  overflow: hidden;
}

.chart-description {
  margin-top: 12px;
  padding: 10px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 12px;
  color: #606266;
  line-height: 1.6;
}

.metrics-description {
  margin-top: 16px;
  padding: 12px 16px;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #409eff;
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
}

.expand-btn {
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 100;
  background: white;
  border: 1px solid #dcdfe6;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
}

.expand-btn:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.expanded-chart-container {
  height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.expanded-chart-container :deep(.el-card) {
  width: 100%;
  height: 100%;
  max-height: 100%;
}

.expanded-chart-container :deep(.el-card__body) {
  height: calc(100% - 60px);
}

/* Улучшаем читаемость таблицы с метриками */
:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table td) {
  padding: 12px 0;
}

:deep(.el-table .cell) {
  line-height: 1.6;
}
</style>
