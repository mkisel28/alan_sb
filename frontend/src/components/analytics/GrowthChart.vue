<template>
  <el-card>
    <template #header>
      <span class="font-medium">Рост показателей</span>
    </template>
    
    <Bar :data="chartData" :options="chartOptions" />
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
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

const chartData = computed(() => {
  if (!props.data?.comparison || !props.data?.current_period) return { labels: [], datasets: [] }
  
  const comp = props.data.comparison
  const current = props.data.current_period.metrics
  
  // Вычисляем процент изменения публикаций
  const prevPosts = props.data.previous_period?.metrics?.P || 0
  const currentPosts = current.P || 0
  const postsChangePercent = prevPosts > 0 ? ((currentPosts - prevPosts) / prevPosts) * 100 : 0
  
  return {
    labels: ['Подписчики', 'Публикации', 'Просмотры', 'Вовлеченность'],
    datasets: [
      {
        label: 'Изменение (%)',
        data: [
          current.delta_F_percent || 0,
          postsChangePercent,
          comp.V_change_percent || 0,
          comp.E_change_percent || 0
        ],
        backgroundColor: function(context) {
          const value = context.parsed.y
          if (value > 0) return 'rgba(82, 196, 26, 0.8)'
          if (value < 0) return 'rgba(245, 34, 45, 0.8)'
          return 'rgba(128, 128, 128, 0.8)'
        },
        borderColor: function(context) {
          const value = context.parsed.y
          if (value > 0) return 'rgb(82, 196, 26)'
          if (value < 0) return 'rgb(245, 34, 45)'
          return 'rgb(128, 128, 128)'
        },
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
      display: false
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || ''
          if (label) {
            label += ': '
          }
          const value = context.parsed.y
          label += (value > 0 ? '+' : '') + value.toFixed(1) + '%'
          return label
        }
      }
    }
  },
  scales: {
    y: {
      ticks: {
        callback: function(value) {
          return value.toFixed(0) + '%'
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
