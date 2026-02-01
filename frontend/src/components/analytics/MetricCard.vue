<template>
  <el-card class="metric-card" :class="`metric-card-${color}`">
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <div class="text-sm text-gray-600 mb-1">{{ title }}</div>
        <div class="text-2xl font-bold">{{ value }}</div>
        
        <div v-if="change !== undefined || changePercent !== undefined" class="flex items-center gap-1 mt-2">
          <el-icon v-if="isPositive" class="text-green-500"><CaretTop /></el-icon>
          <el-icon v-else-if="isNegative" class="text-red-500"><CaretBottom /></el-icon>
          <el-icon v-else class="text-gray-400"><Minus /></el-icon>
          
          <span :class="changeClass" class="text-sm font-medium">
            <template v-if="change !== undefined">
              {{ formatChange(change) }}
            </template>
            <template v-if="changePercent !== undefined">
              {{ formatChangePercent(changePercent) }}
            </template>
          </span>
        </div>
      </div>
      
      <div :class="`icon-wrapper icon-${color}`">
        <el-icon :size="24">
          <component :is="iconComponent" />
        </el-icon>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { CaretTop, CaretBottom, Minus } from '@element-plus/icons-vue'
import * as Icons from '@element-plus/icons-vue'

const props = defineProps({
  title: String,
  value: [String, Number],
  change: Number,
  changePercent: Number,
  icon: String,
  color: {
    type: String,
    default: 'blue'
  }
})

const iconComponent = computed(() => Icons[props.icon] || Icons.DataLine)

const isPositive = computed(() => {
  const val = props.change !== undefined ? props.change : props.changePercent
  return val > 0
})

const isNegative = computed(() => {
  const val = props.change !== undefined ? props.change : props.changePercent
  return val < 0
})

const changeClass = computed(() => {
  if (isPositive.value) return 'text-green-600'
  if (isNegative.value) return 'text-red-600'
  return 'text-gray-500'
})

const formatChange = (val) => {
  if (!val && val !== 0) return ''
  const sign = val > 0 ? '+' : ''
  return `${sign}${val.toLocaleString()}`
}

const formatChangePercent = (val) => {
  if (!val && val !== 0) return ''
  const sign = val > 0 ? '+' : ''
  return `${sign}${val.toFixed(1)}%`
}
</script>

<style scoped>
.metric-card {
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
    justify-content: center;
}

.icon-blue { background: rgba(64, 158, 255, 0.1); color: #409eff; }
.icon-purple { background: rgba(114, 46, 209, 0.1); color: #722ed1; }
.icon-green { background: rgba(82, 196, 26, 0.1); color: #52c41a; }
.icon-cyan { background: rgba(19, 194, 194, 0.1); color: #13c2c2; }
.icon-orange { background: rgba(250, 140, 22, 0.1); color: #fa8c16; }
.icon-pink { background: rgba(235, 47, 150, 0.1); color: #eb2f96; }
</style>
