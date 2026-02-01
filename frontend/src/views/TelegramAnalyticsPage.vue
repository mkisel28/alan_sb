<template>
  <div class="p-3 md:p-6 bg-gray-50 min-h-screen">
    <!-- Заголовок -->
    <div class="mb-4 md:mb-6">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-2">📊 Аналитика Telegram каналов</h1>
      <p class="text-sm md:text-base text-gray-600">Детальная аналитика по всем авторам с Telegram каналами</p>
    </div>

    <!-- Фильтры -->
    <el-card class="mb-4 md:mb-6">
      <el-form :inline="true" class="flex flex-wrap gap-4">
        <el-form-item label="Период">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="—"
            start-placeholder="Начало"
            end-placeholder="Конец"
            format="DD.MM.YYYY HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 350px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadAnalytics" :loading="loading">
            <el-icon><Refresh /></el-icon>
            Загрузить аналитику
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Кнопка экспорта -->
    <div v-if="!loading && analyticsData" class="mb-4 md:mb-6">
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
            <span class="text-sm font-semibold">
              Всего авторов: {{ analyticsData.authors_count }} | Всего каналов: {{ analyticsData.total_aggregated.total_channels }}
            </span>
          </div>
        </template>
      </el-alert>
    </div>

    <!-- Общая статистика -->
    <div v-if="!loading && analyticsData" class="mb-6">
      <el-card>
        <template #header>
          <div class="text-xl font-bold">Общая статистика по всем авторам</div>
        </template>
        
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
          <div class="stat-block">
            <div class="stat-label">Подписчики</div>
            <div class="stat-value">{{ formatNumber(analyticsData.total_aggregated.F) }}</div>
          </div>
          <div class="stat-block">
            <div class="stat-label">Публикации</div>
            <div class="stat-value">{{ analyticsData.total_aggregated.P }}</div>
          </div>
          <div class="stat-block">
            <div class="stat-label">Просмотры</div>
            <div class="stat-value">{{ formatNumber(analyticsData.total_aggregated.V) }}</div>
          </div>
          <div class="stat-block">
            <div class="stat-label">Вовлечения</div>
            <div class="stat-value">{{ formatNumber(analyticsData.total_aggregated.E) }}</div>
          </div>
          <div class="stat-block">
            <div class="stat-label">ER view %</div>
            <div class="stat-value">{{ (analyticsData.total_aggregated.ER_view * 100).toFixed(2) }}%</div>
          </div>
          <div class="stat-block">
            <div class="stat-label">Средний ERR%</div>
            <div class="stat-value">{{ analyticsData.total_aggregated.err_percent_avg?.toFixed(2) }}%</div>
          </div>
          <div class="stat-block">
            <div class="stat-label">Средний ER%</div>
            <div class="stat-value">{{ analyticsData.total_aggregated.er_percent_avg?.toFixed(2) }}%</div>
          </div>
          <div class="stat-block">
            <div class="stat-label">Средний охват поста</div>
            <div class="stat-value">{{ formatNumber(analyticsData.total_aggregated.avg_post_reach_avg) }}</div>
          </div>
          <div class="stat-block">
            <div class="stat-label">Средний ИЦ</div>
            <div class="stat-value">{{ analyticsData.total_aggregated.ci_index_avg?.toFixed(2) }}</div>
          </div>
          <div class="stat-block">
            <div class="stat-label">Реакции</div>
            <div class="stat-value">{{ formatNumber(analyticsData.total_aggregated.total_reactions) }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Блоки по авторам -->
    <div v-if="!loading && analyticsData" class="space-y-6">
      <div
        v-for="authorData in analyticsData.authors"
        :key="authorData.author_id"
        class="author-block"
      >
        <!-- Заголовок автора -->
        <div class="rounded-t-xl p-4 md:p-6 bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <div class="flex justify-between items-center">
            <div>
              <h2 class="text-xl md:text-2xl font-bold mb-2">{{ authorData.author_name }}</h2>
              <p class="text-sm md:text-base text-white/90">{{ authorData.aggregated_metrics.channels_count }} каналов</p>
            </div>
            <div class="text-right">
              <div class="text-2xl md:text-3xl font-bold">{{ authorData.aggregated_metrics.err_percent_avg?.toFixed(2) }}%</div>
              <div class="text-xs md:text-sm text-white/90">Средний ERR%</div>
            </div>
          </div>

          <!-- Агрегированная статистика автора -->
          <div class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mt-4">
            <div class="bg-white/20 rounded-lg p-3">
              <div class="text-xl md:text-2xl font-bold">{{ formatNumber(authorData.aggregated_metrics.F) }}</div>
              <div class="text-xs md:text-sm text-white/90">Подписчиков</div>
            </div>
            <div class="bg-white/20 rounded-lg p-3">
              <div class="text-xl md:text-2xl font-bold">{{ authorData.aggregated_metrics.P }}</div>
              <div class="text-xs md:text-sm text-white/90">Публикаций</div>
            </div>
            <div class="bg-white/20 rounded-lg p-3">
              <div class="text-xl md:text-2xl font-bold">{{ formatNumber(authorData.aggregated_metrics.V) }}</div>
              <div class="text-xs md:text-sm text-white/90">Просмотров</div>
            </div>
            <div class="bg-white/20 rounded-lg p-3">
              <div class="text-xl md:text-2xl font-bold">{{ (authorData.aggregated_metrics.ER_view * 100).toFixed(2) }}%</div>
              <div class="text-xs md:text-sm text-white/90">ER view</div>
            </div>
          </div>
        </div>

        <!-- Таблица каналов автора -->
        <div class="bg-white rounded-b-xl p-4 md:p-6 shadow-sm">
          <h3 class="text-lg font-semibold mb-4">Детализация по каналам</h3>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Канал</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Подписчики</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Посты</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Просмотры</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ср. просмотры</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">ERR%</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">ER%</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">ИЦ</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Реакции</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="channel in authorData.channels" :key="channel.social_account_id" class="hover:bg-gray-50">
                  <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                    @{{ channel.username }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    {{ formatNumber(channel.metrics.F) }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    {{ channel.metrics.P }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    {{ formatNumber(channel.metrics.V) }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    {{ formatNumber(channel.metrics.V_avg) }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-right">
                    <span class="text-blue-600 font-semibold">{{ channel.metrics.ERR_percent?.toFixed(2) }}%</span>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-right">
                    <span class="text-purple-600 font-semibold">{{ channel.metrics.ER_percent?.toFixed(2) }}%</span>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    {{ channel.metrics.ci_index?.toFixed(2) }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    {{ formatNumber(channel.metrics.total_reactions) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-20">
      <el-icon class="is-loading" :size="50"><Loading /></el-icon>
    </div>

    <!-- Заглушка если нет данных -->
    <el-empty v-if="!loading && !analyticsData" description="Выберите период и нажмите 'Загрузить аналитику'" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Refresh, Loading } from '@element-plus/icons-vue'
import api from '@/api'
import dayjs from 'dayjs'

const dateRange = ref([])
const loading = ref(false)
const exportingExcel = ref(false)
const analyticsData = ref(null)

onMounted(() => {
  // Устанавливаем дефолтный период - последние 30 дней
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  dateRange.value = [
    dayjs(start).format('YYYY-MM-DDTHH:mm:ss'),
    dayjs(end).format('YYYY-MM-DDTHH:mm:ss')
  ]
})

const loadAnalytics = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('Выберите период')
    return
  }

  loading.value = true
  try {
    analyticsData.value = await api.getAllAuthorsTelegramAnalytics(
      dateRange.value[0],
      dateRange.value[1]
    )
    
    if (analyticsData.value.authors_count === 0) {
      ElMessage.info('Не найдено авторов с активными Telegram каналами')
    }
  } catch (error) {
    ElMessage.error('Ошибка загрузки аналитики')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const downloadExcelReport = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('Выберите период')
    return
  }

  exportingExcel.value = true
  try {
    const blob = await api.exportAllAuthorsTelegramExcel(
      dateRange.value[0],
      dateRange.value[1]
    )
    
    // Создаем ссылку для скачивания
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `telegram_all_authors_${dayjs(dateRange.value[0]).format('YYYY-MM-DD')}_to_${dayjs(dateRange.value[1]).format('YYYY-MM-DD')}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('Excel отчет скачан')
  } catch (error) {
    ElMessage.error('Ошибка экспорта данных')
    console.error(error)
  } finally {
    exportingExcel.value = false
  }
}

const formatNumber = (num) => {
  return new Intl.NumberFormat('ru-RU').format(Math.round(num || 0))
}

const formatDate = (dateStr) => {
  return dayjs(dateStr).format('DD.MM.YYYY HH:mm')
}
</script>

<style scoped>
.stat-block {
  @apply bg-gray-50 rounded-lg p-4 text-center;
}

.stat-label {
  @apply text-sm text-gray-600 mb-2;
}

.stat-value {
  @apply text-2xl font-bold text-gray-900;
}

.author-block {
  @apply bg-white rounded-xl shadow-md overflow-hidden;
}

@media (max-width: 768px) {
  .stat-value {
    @apply text-xl;
  }
  
  table {
    @apply text-xs;
  }
}
</style>
