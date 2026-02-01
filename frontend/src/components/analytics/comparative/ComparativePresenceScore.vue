<template>
  <div class="relative" ref="containerRef">
    <el-card class="comparative-chart-card">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-semibold">Presence Score (PS) - Сила присутствия</span>
          <el-tag size="small">0-100</el-tag>
        </div>
      </template>
      <div class="chart-container">
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
      <strong>Формула:</strong> PS = 0.25·pct(V_avg) + 0.25·pct(ER_view) + 0.15·pct(SR) + 0.10·pct(P) + 0.25·pct(F)
      <br>Где F - количество подписчиков (масштаб влияния). Перцентильный рейтинг среди всех авторов платформы
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

  // Фильтруем и сортируем по PS
  const filteredAuthors = props.authors.filter(a => selectedAuthors.value.includes(a.author_id))
  if (filteredAuthors.length === 0) return
  
  const sortedAuthors = [...filteredAuthors].sort((a, b) => 
    b.scores.PS - a.scores.PS
  )

  const labels = sortedAuthors.map(a => a.author_name)
  
  // Проверяем наличие данных за предыдущий период
  const hasPrevious = sortedAuthors.some(a => a.scores.prev_PS !== undefined)
  
  // Текущие значения PS
  const psValues = sortedAuthors.map(a => a.scores.PS)
  
  // Предыдущие значения PS (если есть)
  const prevPsValues = sortedAuthors.map(a => 
    a.scores.prev_PS !== undefined ? a.scores.prev_PS : null
  )

  // Создаем datasets
  const datasets = [
    {
      label: 'Текущий период',
      data: psValues,
      backgroundColor: 'rgba(138, 43, 226, 0.7)',
      borderColor: 'rgba(138, 43, 226, 1)',
      borderWidth: 2
    }
  ]

  if (hasPrevious) {
    datasets.push({
      label: 'Предыдущий период',
      data: prevPsValues,
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
          display: hasPrevious
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const author = sortedAuthors[context.dataIndex]
              const isPrevious = context.datasetIndex === 1
              
              if (isPrevious) {
                const result = [
                  `Предыдущий период: ${context.parsed.y.toFixed(1)}`
                ]
                if (author.scores.prev_percentiles) {
                  result.push('Перцентили (предыдущий период):')
                  result.push(`  V_avg: ${author.scores.prev_percentiles.V_avg}`)
                  result.push(`  ER_view: ${author.scores.prev_percentiles.ER_view}`)
                  result.push(`  SR: ${author.scores.prev_percentiles.SR}`)
                  result.push(`  P: ${author.scores.prev_percentiles.P}`)
                  result.push(`  F: ${author.scores.prev_percentiles.F}`)
                }
                return result
              }
              
              const result = [
                `Текущий период: ${context.parsed.y.toFixed(1)}`
              ]
              
              if (author.scores.percentiles) {
                result.push('Перцентили:')
                result.push(`  V_avg: ${author.scores.percentiles.V_avg}`)
                result.push(`  ER_view: ${author.scores.percentiles.ER_view}`)
                result.push(`  SR: ${author.scores.percentiles.SR}`)
                result.push(`  P: ${author.scores.percentiles.P}`)
                result.push(`  F: ${author.scores.percentiles.F}`)
              }
              
              // Добавляем изменение PS если есть предыдущий период
              if (author.scores.prev_PS !== undefined) {
                const delta = author.scores.PS - author.scores.prev_PS
                result.push(`Изменение: ${delta > 0 ? '+' : ''}${delta.toFixed(1)} баллов`)
              }
              
              return result
            }
          }
        }
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: {
            stepSize: 20
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
