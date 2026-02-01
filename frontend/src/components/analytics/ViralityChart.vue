<template>
  <el-card>
    <template #header>
      <span class="font-medium">Виральность контента</span>
    </template>
    
    <Radar :data="chartData" :options="chartOptions" />
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

const props = defineProps({
  data: Object
})

const chartData = computed(() => {
  if (!props.data) return { labels: [], datasets: [] }
  
  const currentData = props.data.current_period.metrics
  const previousData = props.data.previous_period?.metrics
  
  return {
    labels: ['Share Rate (%)', 'Comment Rate (%)', 'ER View (%)', 'ER Fol (%)'],
    datasets: [
      {
        label: 'Текущий период',
        data: [
          currentData.SR || 0,
          currentData.CR || 0,
          currentData.ER_view || 0,
          currentData.ER_fol || 0
        ],
        backgroundColor: 'rgba(82, 196, 26, 0.2)',
        borderColor: 'rgb(82, 196, 26)',
        pointBackgroundColor: 'rgb(82, 196, 26)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(82, 196, 26)'
      },
      ...(previousData ? [{
        label: 'Предыдущий период',
        data: [
          previousData.SR || 0,
          previousData.CR || 0,
          previousData.ER_view || 0,
          previousData.ER_fol || 0
        ],
        backgroundColor: 'rgba(64, 158, 255, 0.2)',
        borderColor: 'rgb(64, 158, 255)',
        pointBackgroundColor: 'rgb(64, 158, 255)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(64, 158, 255)'
      }] : [])
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
          label += context.parsed.r.toFixed(2) + '%'
          return label
        }
      }
    }
  },
  scales: {
    r: {
      beginAtZero: true,
      ticks: {
        callback: function(value) {
          return value.toFixed(1) + '%'
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
