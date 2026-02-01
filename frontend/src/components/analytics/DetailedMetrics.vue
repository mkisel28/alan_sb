<template>
  <el-card>
    <template #header>
      <span class="font-medium">Детальные метрики</span>
    </template>
    
    <el-table :data="tableData" stripe>
      <el-table-column prop="metric" label="Метрика" width="250" />
      <el-table-column label="Текущий период" align="right">
        <template #default="{ row }">
          <span class="font-medium">{{ row.current }}</span>
        </template>
      </el-table-column>
      <el-table-column v-if="showComparison" label="Предыдущий период" align="right">
        <template #default="{ row }">
          <span>{{ row.previous }}</span>
        </template>
      </el-table-column>
      <el-table-column v-if="showComparison" label="Изменение" align="right" width="150">
        <template #default="{ row }">
          <div v-if="row.change !== undefined" class="flex items-center justify-end gap-1">
            <el-icon v-if="row.change > 0" class="text-green-500"><CaretTop /></el-icon>
            <el-icon v-else-if="row.change < 0" class="text-red-500"><CaretBottom /></el-icon>
            <el-icon v-else class="text-gray-400"><Minus /></el-icon>
            <span :class="row.change > 0 ? 'text-green-600' : row.change < 0 ? 'text-red-600' : 'text-gray-500'">
              {{ row.changeText }}
            </span>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { CaretTop, CaretBottom, Minus } from '@element-plus/icons-vue'

const props = defineProps({
  data: Object
})

const showComparison = computed(() => !!props.data?.previous)

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

const formatChange = (value, isPercent = false) => {
  if (value === null || value === undefined || value === 0) return '0'
  const sign = value > 0 ? '+' : ''
  if (isPercent) {
    return sign + value.toFixed(1) + '%'
  }
  return sign + formatNumber(Math.abs(value))
}

const tableData = computed(() => {
  if (!props.data) return []
  
  const current = props.data.current_period.metrics
  const previous = props.data.previous_period?.metrics
  const comparison = props.data.comparison
  
  const metrics = [
    {
      metric: 'Подписчики (F)',
      current: formatNumber(current.F),
      previous: previous ? formatNumber(previous.F) : '-',
      change: comparison?.followers_change,
      changeText: formatChange(comparison?.followers_change)
    },
    {
      metric: 'Изменение подписчиков (ΔF)',
      current: formatNumber(current.delta_F),
      previous: previous ? formatNumber(previous.delta_F) : '-',
      change: comparison?.followers_change,
      changeText: formatChange(comparison?.followers_change)
    },
    {
      metric: 'Изменение подписчиков (ΔF%)',
      current: formatPercent(current.delta_F_percent),
      previous: previous ? formatPercent(previous.delta_F_percent) : '-',
      change: comparison?.followers_change_percent,
      changeText: formatChange(comparison?.followers_change_percent, true)
    },
    {
      metric: 'Публикации (P)',
      current: current.P,
      previous: previous ? previous.P : '-',
      change: comparison?.posts_change,
      changeText: formatChange(comparison?.posts_change)
    },
    {
      metric: 'Общие просмотры (V)',
      current: formatNumber(current.V),
      previous: previous ? formatNumber(previous.V) : '-',
      change: comparison?.views_change,
      changeText: formatChange(comparison?.views_change)
    },
    {
      metric: 'Средние просмотры (V_avg)',
      current: formatNumber(current.V_avg),
      previous: previous ? formatNumber(previous.V_avg) : '-',
      change: comparison?.views_change,
      changeText: formatChange(comparison?.views_change)
    },
    {
      metric: 'Медианные просмотры (V_median)',
      current: formatNumber(current.V_median),
      previous: previous ? formatNumber(previous.V_median) : '-'
    },
    {
      metric: 'Общая вовлеченность (E)',
      current: formatNumber(current.E),
      previous: previous ? formatNumber(previous.E) : '-',
      change: comparison?.engagement_change,
      changeText: formatChange(comparison?.engagement_change)
    },
    {
      metric: 'Средняя вовлеченность (E_avg)',
      current: formatNumber(current.E_avg),
      previous: previous ? formatNumber(previous.E_avg) : '-',
      change: comparison?.engagement_change,
      changeText: formatChange(comparison?.engagement_change)
    },
    {
      metric: 'Медианная вовлеченность (E_median)',
      current: formatNumber(current.E_median),
      previous: previous ? formatNumber(previous.E_median) : '-'
    },
    {
      metric: 'ER по просмотрам (ER_view)',
      current: formatPercent(current.ER_view),
      previous: previous ? formatPercent(previous.ER_view) : '-'
    },
    {
      metric: 'ER по подписчикам (ER_fol)',
      current: formatPercent(current.ER_fol),
      previous: previous ? formatPercent(previous.ER_fol) : '-'
    },
    {
      metric: 'Share Rate (SR)',
      current: formatPercent(current.SR),
      previous: previous ? formatPercent(previous.SR) : '-'
    },
    {
      metric: 'Comment Rate (CR)',
      current: formatPercent(current.CR),
      previous: previous ? formatPercent(previous.CR) : '-'
    }
  ]
  
  return metrics
})
</script>

<style scoped>
.el-table {
  font-size: 14px;
}
</style>
