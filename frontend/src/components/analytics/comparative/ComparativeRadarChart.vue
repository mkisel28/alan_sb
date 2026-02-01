<template>
  <div class="relative" ref="containerRef">
    <el-card class="comparative-chart-card">
      <template #header>
        <div class="flex justify-between items-center flex-wrap gap-2">
          <span class="font-semibold">Радар метрик - Многомерное сравнение</span>
          <div class="flex items-center gap-2">
            <el-select
              v-model="selectedAuthors"
              multiple
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="2"
              placeholder="Выберите авторов"
              class="w-64"
              @change="createChart"
            >
              <el-option
                v-for="author in sortedAuthors"
                :key="author.social_account_id"
                :label="author.author_name"
                :value="author.social_account_id"
              />
            </el-select>
            <el-button
              size="small"
              @click="selectTopAuthors"
              title="Выбрать топ-5"
            >
              Топ-5
            </el-button>
            <el-button
              size="small"
              @click="selectAll"
              title="Выбрать всех"
            >
              Все
            </el-button>
          </div>
        </div>
      </template>
      <div v-if="selectedAuthors.length > 0" class="chart-container">
        <canvas ref="chartCanvas"></canvas>
      </div>
      <el-empty v-else description="Выберите авторов для сравнения" />
      <el-button
        v-if="selectedAuthors.length > 0"
        class="fullscreen-btn"
        :icon="FullScreen"
        circle
        size="small"
        @click="toggleFullscreen"
        title="Развернуть на весь экран"
      />
    </el-card>
    <div class="mt-2 text-sm text-gray-600">
      <strong>Показатели:</strong> V_avg, ER_view, SR, P, F (подписчики), PS - нормализованы от 0 до 100 (перцентили)
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue'
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
let chartInstance = null
const selectedAuthors = ref([])

const sortedAuthors = computed(() => {
  return [...props.authors].sort((a, b) => b.scores.PS - a.scores.PS)
})

const selectTopAuthors = () => {
  selectedAuthors.value = sortedAuthors.value.slice(0, 5).map(a => a.social_account_id)
  createChart()
}

const selectAll = () => {
  selectedAuthors.value = sortedAuthors.value.map(a => a.social_account_id)
  createChart()
}

const createChart = () => {
  if (!chartCanvas.value || selectedAuthors.value.length === 0) return

  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')

  // Получаем выбранных авторов
  const authorsToShow = props.authors.filter(a => 
    selectedAuthors.value.includes(a.social_account_id)
  )

  // Нормализуем метрики для каждого автора
  const datasets = authorsToShow.map((author, index) => {
    const colors = [
      'rgba(255, 99, 132, 0.5)',
      'rgba(54, 162, 235, 0.5)',
      'rgba(255, 206, 86, 0.5)',
      'rgba(75, 192, 192, 0.5)',
      'rgba(153, 102, 255, 0.5)',
      'rgba(255, 159, 64, 0.5)',
      'rgba(199, 199, 199, 0.5)',
      'rgba(83, 102, 255, 0.5)',
      'rgba(255, 102, 255, 0.5)',
      'rgba(102, 255, 178, 0.5)'
    ]
    
    const borderColors = [
      'rgba(255, 99, 132, 1)',
      'rgba(54, 162, 235, 1)',
      'rgba(255, 206, 86, 1)',
      'rgba(75, 192, 192, 1)',
      'rgba(153, 102, 255, 1)',
      'rgba(255, 159, 64, 1)',
      'rgba(199, 199, 199, 1)',
      'rgba(83, 102, 255, 1)',
      'rgba(255, 102, 255, 1)',
      'rgba(102, 255, 178, 1)'
    ]

    return {
      label: author.author_name,
      data: [
        author.scores.percentiles.V_avg,
        author.scores.percentiles.ER_view,
        author.scores.percentiles.SR,
        author.scores.percentiles.P,
        author.scores.percentiles.F,
        author.scores.PS
      ],
      backgroundColor: colors[index % 10],
      borderColor: borderColors[index % 10],
      borderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6
    }
  })

  chartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['V_avg', 'ER_view', 'SR', 'P', 'F (подписчики)', 'PS'],
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
              const author = authorsToShow[context.datasetIndex]
              const labels = ['V_avg', 'ER_view', 'SR', 'P', 'F (подписчики)', 'PS']
              return `${context.dataset.label}: ${context.parsed.r} (перцентиль ${labels[context.dataIndex]})`
            }
          }
        }
      },
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: {
            stepSize: 20
          },
          pointLabels: {
            font: {
              size: 14,
              weight: 'bold'
            }
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
  // При изменении авторов, автоматически выбираем топ-5
  if (props.authors.length > 0 && selectedAuthors.value.length === 0) {
    selectTopAuthors()
  }
}, { deep: true })

onMounted(() => {
  if (props.authors.length > 0) {
    selectTopAuthors()
  }
  
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
  height: 400px;
}

@media (min-width: 768px) {
  .chart-container {
    height: 500px;
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
