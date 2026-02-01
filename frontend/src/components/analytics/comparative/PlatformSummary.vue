<template>
  <el-card class="platform-summary-card">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="metric-item">
        <div class="metric-label">Авторов</div>
        <div class="metric-value">{{ aggregated.total_authors }}</div>
      </div>
      
      <div class="metric-item">
        <div class="metric-label">Всего подписчиков</div>
        <div class="metric-value">{{ formatNumber(aggregated.total_followers) }}</div>
        <div v-if="hasDelta('followers')" class="metric-delta" :class="getDeltaClass('followers')">
          <span class="delta-icon">{{ getDeltaIcon('followers') }}</span>
          {{ formatNumber(aggregated.deltas.followers.absolute) }}
          ({{ formatPercent(aggregated.deltas.followers.percent) }})
        </div>
      </div>
      
      <div class="metric-item">
        <div class="metric-label">Всего постов</div>
        <div class="metric-value">{{ aggregated.total_posts }}</div>
        <div v-if="hasDelta('posts')" class="metric-delta" :class="getDeltaClass('posts')">
          <span class="delta-icon">{{ getDeltaIcon('posts') }}</span>
          {{ aggregated.deltas.posts.absolute }}
          ({{ formatPercent(aggregated.deltas.posts.percent) }})
        </div>
      </div>
      
      <div class="metric-item">
        <div class="metric-label">Всего просмотров</div>
        <div class="metric-value">{{ formatNumber(aggregated.total_views) }}</div>
        <div v-if="hasDelta('views')" class="metric-delta" :class="getDeltaClass('views')">
          <span class="delta-icon">{{ getDeltaIcon('views') }}</span>
          {{ formatNumber(aggregated.deltas.views.absolute) }}
          ({{ formatPercent(aggregated.deltas.views.percent) }})
        </div>
      </div>
      
      <div class="metric-item">
        <div class="metric-label">Всего вовлечений</div>
        <div class="metric-value">{{ formatNumber(aggregated.total_engagement) }}</div>
        <div v-if="hasDelta('engagement')" class="metric-delta" :class="getDeltaClass('engagement')">
          <span class="delta-icon">{{ getDeltaIcon('engagement') }}</span>
          {{ formatNumber(aggregated.deltas.engagement.absolute) }}
          ({{ formatPercent(aggregated.deltas.engagement.percent) }})
        </div>
      </div>
      
      <div class="metric-item">
        <div class="metric-label">Средний PS</div>
        <div class="metric-value">
          <el-tag :type="getScoreType(aggregated.avg_PS)" size="large">
            {{ aggregated.avg_PS }}
          </el-tag>
        </div>
      </div>
      
      <div v-if="aggregated.avg_MS !== undefined" class="metric-item">
        <div class="metric-label">Средний MS</div>
        <div class="metric-value">
          <el-tag :type="getScoreType(aggregated.avg_MS)" size="large">
            {{ aggregated.avg_MS }}
          </el-tag>
        </div>
      </div>
      
      <div class="metric-item">
        <div class="metric-label">Средний ER_view</div>
        <div class="metric-value">{{ (aggregated.avg_ER_view * 100).toFixed(2) }}%</div>
        <div v-if="hasDelta('ER_view')" class="metric-delta" :class="getDeltaClass('ER_view')">
          <span class="delta-icon">{{ getDeltaIcon('ER_view') }}</span>
          {{ (aggregated.deltas.ER_view.absolute * 100).toFixed(2) }}%
          ({{ formatPercent(aggregated.deltas.ER_view.percent) }})
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
const props = defineProps({
  aggregated: {
    type: Object,
    required: true
  }
})

const formatNumber = (num) => {
  if (num === undefined || num === null) return '0'
  return Math.round(num).toLocaleString('ru-RU')
}

const formatPercent = (percent) => {
  if (percent === undefined || percent === null) return '0%'
  const sign = percent > 0 ? '+' : ''
  return `${sign}${percent.toFixed(1)}%`
}

const hasDelta = (metric) => {
  return props.aggregated.deltas && props.aggregated.deltas[metric]
}

const getDeltaClass = (metric) => {
  if (!hasDelta(metric)) return ''
  const value = props.aggregated.deltas[metric].absolute
  return value > 0 ? 'delta-positive' : value < 0 ? 'delta-negative' : 'delta-neutral'
}

const getDeltaIcon = (metric) => {
  if (!hasDelta(metric)) return ''
  const value = props.aggregated.deltas[metric].absolute
  return value > 0 ? '↑' : value < 0 ? '↓' : '='
}

const getScoreType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'primary'
  if (score >= 40) return 'warning'
  return 'danger'
}
</script>

<style scoped>
.platform-summary-card {
  margin-bottom: 1.5rem;
}

.metric-item {
  text-align: center;
  padding: 1rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
  transition: transform 0.2s;
}

.metric-item:hover {
  transform: translateY(-2px);
}

.metric-label {
  font-size: 0.875rem;
  color: #606266;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #303133;
  margin-bottom: 0.25rem;
}

.metric-delta {
  font-size: 0.75rem;
  font-weight: 600;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.delta-icon {
  font-size: 1rem;
  font-weight: bold;
}

.delta-positive {
  color: #67c23a;
}

.delta-negative {
  color: #f56c6c;
}

.delta-neutral {
  color: #909399;
}
</style>
