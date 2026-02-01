<template>
  <div class="relative" ref="containerRef">
    <el-card class="comparative-chart-card">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-semibold">Momentum Score (MS) - Ускорение роста</span>
          <el-tag size="small" type="warning">0-100</el-tag>
        </div>
      </template>
      <div v-if="hasMS" class="mb-3">
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
      </div>
      <div v-if="hasMS" class="chart-container">
        <canvas ref="chartCanvas"></canvas>
      </div>
      <el-empty v-else description="Включите предыдущий период для расчета MS" />
      <el-button
        v-if="hasMS"
        class="fullscreen-btn"
        :icon="FullScreen"
        circle
        size="small"
        @click="toggleFullscreen"
        title="Развернуть на весь экран"
      />
    </el-card>
    <div v-if="hasMS" class="mt-2 text-sm text-gray-600">
      <strong>Формула:</strong> MS = 0.50·pct(ΔV_avg%) + 0.30·pct(ΔER%) + 0.20·pct(ΔF%)
      <br>Показывает динамику роста относительно других авторов
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
const selectedAuthors = ref([])
let chartInstance = null

const hasMS = computed(() => {
  return props.authors.length > 0 && props.authors[0].scores.MS !== undefined
})

// Инициализируем выбор всех авторов при монтировании
watch(() => props.authors, (newAuthors) => {
  if (newAuthors.length > 0 && selectedAuthors.value.length === 0) {
    selectedAuthors.value = newAuthors.map(a => a.author_id)
  }
}, { immediate: true })

// Пересоздаем график при изменении выбора авторов
watch(selectedAuthors, () => {
  if (hasMS.value) {
    createChart()
  }
})

const createChart = () => {
  if (!chartCanvas.value || !hasMS.value) return

  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')

  // Фильтруем и сортируем по MS
  const filteredAuthors = props.authors.filter(a => selectedAuthors.value.includes(a.author_id))
  if (filteredAuthors.length === 0) return
  
  const sortedAuthors = [...filteredAuthors].sort((a, b) => 
    (b.scores.MS || 0) - (a.scores.MS || 0)
  )

  const labels = sortedAuthors.map(a => a.author_name)
  const msValues = sortedAuthors.map(a => a.scores.MS || 0)

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Momentum Score',
        data: msValues,
        backgroundColor: 'rgba(230, 162, 60, 0.7)',
        borderColor: 'rgba(230, 162, 60, 1)',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const author = sortedAuthors[context.dataIndex]
              if (!author.scores.momentum_percentiles) {
                return `MS: ${context.parsed.y.toFixed(1)}`
              }
              return [
                `MS: ${context.parsed.y.toFixed(1)}`,
                `Перцентили роста:`,
                `  ΔV_avg: ${author.scores.momentum_percentiles.delta_V_avg}`,
                `  ΔER: ${author.scores.momentum_percentiles.delta_ER}`,
                `  ΔF: ${author.scores.momentum_percentiles.delta_F}`
              ]
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
  if (hasMS.value) {
    createChart()
  }
}, { deep: true })

onMounted(() => {
  if (hasMS.value) {
    createChart()
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
