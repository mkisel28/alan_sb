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

        <!-- Дата начала -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Дата начала</label>
          <el-date-picker
            :model-value="startDate"
            @update:model-value="$emit('update:startDate', $event)"
            type="date"
            placeholder="Выберите дату начала"
            class="w-full"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </div>

        <!-- Дата окончания -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Дата окончания</label>
          <el-date-picker
            :model-value="endDate"
            @update:model-value="$emit('update:endDate', $event)"
            type="date"
            placeholder="Выберите дату окончания"
            class="w-full"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
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
  startDate: {
    type: String,
    default: null
  },
  endDate: {
    type: String,
    default: null
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

defineEmits(['update:platforms', 'update:startDate', 'update:endDate', 'update:includePrevious', 'load'])

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
