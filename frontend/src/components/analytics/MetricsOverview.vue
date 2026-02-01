<template>
  <div>
    <!-- Основные метрики карточками -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <MetricCard
        title="Подписчики"
        :value="formatNumber(data.current_period.metrics.F)"
        :change="data.comparison?.followers_change"
        :changePercent="data.comparison?.followers_change_percent"
        icon="User"
        color="blue"
      />
      
      <MetricCard
        title="Публикации"
        :value="data.current_period.metrics.P"
        :change="data.comparison?.posts_change"
        :changePercent="data.comparison?.posts_change_percent"
        icon="Document"
        color="purple"
      />
      
      <MetricCard
        title="Просмотры"
        :value="formatNumber(data.current_period.metrics.V)"
        :change="data.comparison?.views_change"
        :changePercent="data.comparison?.views_change_percent"
        icon="View"
        color="green"
      />
      
      <MetricCard
        title="Средние просмотры"
        :value="formatNumber(data.current_period.metrics.V_avg)"
        icon="TrendCharts"
        color="cyan"
      />
      
      <MetricCard
        title="Вовлеченность"
        :value="formatNumber(data.current_period.metrics.E)"
        :change="data.comparison?.engagement_change"
        :changePercent="data.comparison?.engagement_change_percent"
        icon="ChatDotRound"
        color="orange"
      />
      
      <MetricCard
        title="ER по просмотрам"
        :value="formatPercent(data.current_period.metrics.ER_view)"
        icon="DataAnalysis"
        color="pink"
      />
    </div>

    <!-- Дополнительная статистика -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="text-sm text-gray-600 mb-1">Средняя вовлеченность</div>
        <div class="text-xl font-semibold">{{ formatNumber(data.current_period.metrics.E_avg) }}</div>
      </div>
      
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="text-sm text-gray-600 mb-1">ER по подписчикам</div>
        <div class="text-xl font-semibold">{{ formatPercent(data.current_period.metrics.ER_fol) }}</div>
      </div>
      
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="text-sm text-gray-600 mb-1">Share Rate</div>
        <div class="text-xl font-semibold">{{ formatPercent(data.current_period.metrics.SR) }}</div>
      </div>
      
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="text-sm text-gray-600 mb-1">Comment Rate</div>
        <div class="text-xl font-semibold">{{ formatPercent(data.current_period.metrics.CR) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import MetricCard from './MetricCard.vue'

defineProps({
  data: Object
})

const formatNumber = (value) => {
  if (value === null || value === undefined) return '-'
  if (value >= 1000000) {
    return (value / 1000000).toFixed(2) + 'M'
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  }
  return value.toLocaleString()
}

const formatPercent = (value) => {
  if (value === null || value === undefined) return '-'
  return value.toFixed(2) + '%'
}
</script>
