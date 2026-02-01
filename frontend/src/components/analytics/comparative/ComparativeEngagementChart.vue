<template>
  <div class="relative" ref="containerRef">
    <el-card class="comparative-chart-card">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-semibold">Вовлеченность (ER_view)</span>
          <el-tag size="small">{{ authors.length }} авторов</el-tag>
        </div>
      </template>      <div class="mb-3">
        <el-select
          v-model="selectedAuthors"
          multiple
          collapse-tags
          collapse-tags-tooltip
          placeholder="Выберите авторов"
          style="width: 100%"
          size="small"
        >
          <el-option
            v-for="author in authors"
            :key="author.author_id"
            :label="author.author_name"
            :value="author.author_id"
          />
        </el-select>
      </div>      <div class="chart-container">
        <canvas ref="chartCanvas"></canvas>
      </div>
      <el-button
        class="fullscreen-btn"
        :icon="FullScreen"
        circle
        size="small"
        @click="toggleFullscreen"
        title="Развернуть на весь экран"
      />
    </el-card>
    <div class="mt-2 text-sm text-gray-600">
      <strong>Формула:</strong> ER_view = (E / V) × 100%, где E = лайки + комменты + шеры + сохранения
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'
import { FullScreen } from '@element-plus/icons-vue'

Chart.register(...registerables)

const props = defineProps({
  authors: {
    type: Array,
    required: true
  }
})

const chartCanvas = ref(null)
const containerRef = ref(null)
const selectedAuthors = ref([])
let chartInstance = null

// Инициализируем выбор всех авторов при монтировании
watch(() => props.authors, (newAuthors) => {
  if (newAuthors.length > 0 && selectedAuthors.value.length === 0) {
    selectedAuthors.value = newAuthors.map(a => a.author_id)
  }
}, { immediate: true })

// Пересоздаем график при изменении выбора авторов
watch(selectedAuthors, () => {
  createChart()
})

const createChart = () => {
  if (!chartCanvas.value || props.authors.length === 0) return

  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')

  // Фильтруем и сортируем по ER_view
  const filteredAuthors = props.authors.filter(a => selectedAuthors.value.includes(a.author_id))
  if (filteredAuthors.length === 0) return
  
  const sortedAuthors = [...filteredAuthors].sort((a, b) => 
    b.metrics.ER_view - a.metrics.ER_view
  )

  const hasPrevious = sortedAuthors.some(a => a.metrics.prev_metrics)

  const labels = sortedAuthors.map(a => a.author_name)
  const currentValues = sortedAuthors.map(a => (a.metrics.ER_view * 100).toFixed(2))
  const previousValues = hasPrevious
    ? sortedAuthors.map(a => ((a.metrics.prev_metrics?.ER_view || 0) * 100).toFixed(2))
    : []

  const datasets = [{
    label: 'Текущий период',
    data: currentValues,
    backgroundColor: 'rgba(103, 194, 58, 0.7)',
    borderColor: 'rgba(103, 194, 58, 1)',
    borderWidth: 2
  }]

  if (hasPrevious) {
    datasets.push({
      label: 'Предыдущий период',
      data: previousValues,
      backgroundColor: 'rgba(144, 147, 153, 0.5)',
      borderColor: 'rgba(144, 147, 153, 1)',
      borderWidth: 2
    })
  }

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: hasPrevious,
          position: 'top'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const author = sortedAuthors[context.dataIndex]
              const isPrevious = context.datasetIndex === 1
              
              if (isPrevious) {
                return [
                  `${context.dataset.label}: ${context.parsed.y}%`,
                  `Вовлечённость: ${Math.round(author.metrics.prev_metrics?.E || 0).toLocaleString('ru-RU')}`,
                  `Просмотры: ${Math.round(author.metrics.prev_metrics?.V || 0).toLocaleString('ru-RU')}`
                ]
              }
              
              const result = [
                `${context.dataset.label}: ${context.parsed.y}%`,
                `PS: ${author.scores.PS}`,
                `Вовлечённость: ${Math.round(author.metrics.E).toLocaleString('ru-RU')}`,
                `Просмотры: ${Math.round(author.metrics.V).toLocaleString('ru-RU')}`
              ]
              
              if (hasPrevious && author.metrics.delta_ER_percent !== undefined) {
                const change = (author.metrics.delta_ER_percent * 100).toFixed(1)
                result.push(`Изменение: ${change > 0 ? '+' : ''}${change}%`)
              }
              
              return result
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return value + '%'
            }
          }
        },
        x: {
          ticks: {
            autoSkip: false,
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    }
  })
}

const getColorByScore = (score) => {
  if (score >= 80) return 'rgba(103, 194, 58, 0.6)'
  if (score >= 60) return 'rgba(64, 158, 255, 0.6)'
  if (score >= 40) return 'rgba(230, 162, 60, 0.6)'
  return 'rgba(245, 108, 108, 0.6)'
}

const toggleFullscreen = async () => {
  if (containerRef.value) {
    if (!document.fullscreenElement) {
      await containerRef.value.requestFullscreen()
      setTimeout(() => {
        if (chartInstance) {
          chartInstance.resize()
        }
      }, 100)
    } else {
      await document.exitFullscreen()
      setTimeout(() => {
        if (chartInstance) {
          chartInstance.resize()
        }
      }, 100)
    }
  }
}

watch(() => props.authors, () => {
  createChart()
}, { deep: true })

onMounted(() => {
  createChart()
  
  document.addEventListener('fullscreenchange', () => {
    setTimeout(() => {
      if (chartInstance) {
        chartInstance.resize()
      }
    }, 100)
  })
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>

<style scoped>
.comparative-chart-card {
  position: relative;
}

.chart-container {
  position: relative;
  width: 100%;
  height: 350px;
}

@media (min-width: 768px) {
  .chart-container {
    height: 450px;
  }
}

.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

/* Стили для fullscreen режима */
.relative:fullscreen {
  background: white;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.relative:fullscreen .chart-container {
  height: calc(100vh - 200px);
  flex: 1;
}

.relative:fullscreen .comparative-chart-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.fullscreen-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
}
</style>
