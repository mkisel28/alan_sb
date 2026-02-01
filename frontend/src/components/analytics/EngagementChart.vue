<template>
  <el-card>
    <template #header>
      <div class="flex items-center justify-between">
        <span class="font-medium">Вовлеченность</span>
        <el-select v-model="selectedMetric" size="small" style="width: 150px">
          <el-option label="ER по просмотрам" value="er_view" />
          <el-option label="ER по подписчикам" value="er_fol" />
          <el-option label="Средняя вовлеченность" value="e_avg" />
        </el-select>
      </div>
    </template>
    
    <Line :data="chartData" :options="chartOptions" />
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  data: Object
})

const selectedMetric = ref('er_view')

const chartData = computed(() => {
  if (!props.data) return { labels: [], datasets: [] }
  
  const currentData = props.data.current_period.metrics
  const previousData = props.data.previous_period?.metrics
  
  const labels = ['Предыдущий период', 'Текущий период']
  
  let currentValue, previousValue, label
  
  switch (selectedMetric.value) {
    case 'er_view':
      currentValue = currentData.ER_view
      previousValue = previousData?.ER_view
      label = 'ER по просмотрам (%)'
      break
    case 'er_fol':
      currentValue = currentData.ER_fol
      previousValue = previousData?.ER_fol
      label = 'ER по подписчикам (%)'
      break
    case 'e_avg':
      currentValue = currentData.E_avg
      previousValue = previousData?.E_avg
      label = 'Средняя вовлеченность'
      break
  }
  
  return {
    labels,
    datasets: [
      {
        label,
        data: [previousValue || 0, currentValue || 0],
        borderColor: '#722ed1',
        backgroundColor: 'rgba(114, 46, 209, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'bottom'
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || ''
          if (label) {
            label += ': '
          }
          if (selectedMetric.value.startsWith('er_')) {
            label += context.parsed.y.toFixed(2) + '%'
          } else {
            label += context.parsed.y.toLocaleString()
          }
          return label
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: function(value) {
          if (selectedMetric.value.startsWith('er_')) {
            return value.toFixed(1) + '%'
          }
          return value.toLocaleString()
        }
      }
    }
  }
}
</script>

<style scoped>
.el-card {
  height: 400px;
}

.el-card :deep(.el-card__body) {
  height: calc(100% - 60px);
}

@media (min-width: 1024px) {
  .el-card {
    min-height: 400px;
    height: 100%;
  }
}
</style>
