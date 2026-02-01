<template>
  <div class="relative" ref="containerRef">
    <el-card class="comparative-chart-card">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-semibold">Вирусность (SR & CR)</span>
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
      <strong>Формула:</strong> SR = (репосты / просмотры) × 100% | CR = (комменты / просмотры) × 100%
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

  // Фильтруем и сортируем по SR
  const filteredAuthors = props.authors.filter(a => selectedAuthors.value.includes(a.author_id))
  if (filteredAuthors.length === 0) return
  
  const sortedAuthors = [...filteredAuthors].sort((a, b) => 
    b.metrics.SR - a.metrics.SR
  )

  const labels = sortedAuthors.map(a => a.author_name)
  
  // Проверяем наличие данных за предыдущий период
  const hasPrevious = sortedAuthors.some(a => a.metrics.prev_metrics)
  
  // Текущие значения
  const srValues = sortedAuthors.map(a => (a.metrics.SR * 100).toFixed(3))
  const crValues = sortedAuthors.map(a => (a.metrics.CR * 100).toFixed(3))
  
  // Предыдущие значения (если есть)
  const prevSrValues = sortedAuthors.map(a => 
    a.metrics.prev_metrics ? (a.metrics.prev_metrics.SR * 100).toFixed(3) : null
  )
  const prevCrValues = sortedAuthors.map(a => 
    a.metrics.prev_metrics ? (a.metrics.prev_metrics.CR * 100).toFixed(3) : null
  )

  // Создаем datasets
  const datasets = [
    {
      label: 'SR (текущий)',
      data: srValues,
      backgroundColor: 'rgba(255, 99, 132, 0.7)',
      borderColor: 'rgba(255, 99, 132, 1)',
      borderWidth: 2
    },
    {
      label: 'CR (текущий)',
      data: crValues,
      backgroundColor: 'rgba(54, 162, 235, 0.7)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 2
    }
  ]

  if (hasPrevious) {
    datasets.push(
      {
        label: 'SR (предыдущий)',
        data: prevSrValues,
        backgroundColor: 'rgba(255, 99, 132, 0.3)',
        borderColor: 'rgba(255, 99, 132, 0.6)',
        borderWidth: 1
      },
      {
        label: 'CR (предыдущий)',
        data: prevCrValues,
        backgroundColor: 'rgba(54, 162, 235, 0.3)',
        borderColor: 'rgba(54, 162, 235, 0.6)',
        borderWidth: 1
      }
    )
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
          display: true,
          position: 'top'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const author = sortedAuthors[context.dataIndex]
              const isSR = context.datasetIndex === 0 || context.datasetIndex === 2
              const isPrevious = context.datasetIndex >= 2
              
              if (isSR) {
                const result = [
                  `${isPrevious ? 'SR (предыдущий)' : 'SR (текущий)'}: ${context.parsed.y}%`
                ]
                if (!isPrevious) {
                  result.push(`Репосты: ${author.metrics.total_shares.toLocaleString('ru-RU')}`)
                  result.push(`Просмотры: ${Math.round(author.metrics.V).toLocaleString('ru-RU')}`)
                  if (author.metrics.delta_SR_percent !== undefined) {
                    result.push(`Изменение: ${(author.metrics.delta_SR_percent * 100).toFixed(2)}%`)
                  }
                }
                return result
              } else {
                const result = [
                  `${isPrevious ? 'CR (предыдущий)' : 'CR (текущий)'}: ${context.parsed.y}%`
                ]
                if (!isPrevious) {
                  result.push(`Комменты: ${author.metrics.total_comments.toLocaleString('ru-RU')}`)
                  result.push(`Просмотры: ${Math.round(author.metrics.V).toLocaleString('ru-RU')}`)
                  if (author.metrics.delta_CR_percent !== undefined) {
                    result.push(`Изменение: ${(author.metrics.delta_CR_percent * 100).toFixed(2)}%`)
                  }
                }
                return result
              }
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
