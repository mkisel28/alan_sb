<template>
  <el-card>
    <template #header>
      <div class="flex items-center justify-between">
        <span class="font-medium">Просмотры</span>
        <el-select v-model="selectedMetric" size="small" style="width: 180px">
          <el-option label="Общие просмотры" value="v" />
          <el-option label="Средние просмотры" value="v_avg" />
          <el-option label="Медианные просмотры" value="v_median" />
        </el-select>
      </div>
    </template>
    
    <Bar :data="chartData" :options="chartOptions" />
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps({
  data: Object
})

const selectedMetric = ref('v_avg')

const chartData = computed(() => {
  if (!props.data) return { labels: [], datasets: [] }
  
  const currentData = props.data.current_period.metrics
  const previousData = props.data.previous_period?.metrics
  
  const labels = ['Предыдущий период', 'Текущий период']
  
  let currentValue, previousValue, label
  
  switch (selectedMetric.value) {
    case 'v':
      currentValue = currentData.V
      previousValue = previousData?.V
      label = 'Общие просмотры'
      break
    case 'v_avg':
      currentValue = currentData.V_avg
      previousValue = previousData?.V_avg
      label = 'Средние просмотры'
      break
    case 'v_median':
      currentValue = currentData.V_median
      previousValue = previousData?.V_median
      label = 'Медианные просмотры'
      break
  }
  
  return {
    labels,
    datasets: [
      {
        label,
        data: [previousValue || 0, currentValue || 0],
        backgroundColor: [
          'rgba(64, 158, 255, 0.6)',
          'rgba(64, 158, 255, 0.9)'
        ],
        borderColor: [
          'rgb(64, 158, 255)',
          'rgb(64, 158, 255)'
        ],
        borderWidth: 1
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
          label += context.parsed.y.toLocaleString()
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
          if (value >= 1000000) {
            return (value / 1000000).toFixed(1) + 'M'
          } else if (value >= 1000) {
            return (value / 1000).toFixed(0) + 'K'
          }
          return value
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
