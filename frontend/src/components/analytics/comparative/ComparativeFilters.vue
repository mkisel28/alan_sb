<template>
  <div class="mb-6">
    <el-card>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Выбор платформ -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Платформы</label>
          <el-select
            :model-value="selectedPlatforms"
            @update:model-value="$emit('update:platforms', $event)"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="Выберите платформы"
            class="w-full"
          >
            <el-option
              v-for="platform in availablePlatforms"
              :key="platform.value"
              :label="platform.label"
              :value="platform.value"
            />
          </el-select>
        </div>

        <!-- Период -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Период</label>
          <el-select 
            :model-value="period" 
            @update:model-value="$emit('update:period', $event)"
            placeholder="Выберите период" 
            class="w-full"
          >
            <el-option label="7 дней" value="7d" />
            <el-option label="30 дней" value="30d" />
            <el-option label="90 дней" value="90d" />
            <el-option label="365 дней" value="365d" />
          </el-select>
        </div>

        <!-- Предыдущий период -->
        <div class="flex items-end">
          <el-checkbox 
            :model-value="includePrevious"
            @update:model-value="$emit('update:includePrevious', $event)"
          >
            Включить предыдущий период (для MS)
          </el-checkbox>
        </div>

        <!-- Кнопка загрузки -->
        <div class="flex items-end">
          <el-button
            type="primary"
            @click="$emit('load')"
            :loading="loading"
            class="w-full"
          >
            <el-icon class="mr-2"><Refresh /></el-icon>
            Загрузить аналитику
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { Refresh } from '@element-plus/icons-vue'

defineProps({
  selectedPlatforms: {
    type: Array,
    required: true
  },
  period: {
    type: String,
    required: true
  },
  includePrevious: {
    type: Boolean,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:platforms', 'update:period', 'update:includePrevious', 'load'])

const availablePlatforms = [
  { label: 'TikTok', value: 'tiktok' },
  { label: 'YouTube', value: 'youtube' },
  { label: 'YouTube Shorts', value: 'youtube_shorts' },
  { label: 'Instagram', value: 'instagram' },
  { label: 'Facebook', value: 'facebook' },
  { label: 'Twitter/X', value: 'twitter' },
  { label: 'Telegram', value: 'telegram' }
]
</script>

<style scoped>
/* Стили для фильтров */
</style>
