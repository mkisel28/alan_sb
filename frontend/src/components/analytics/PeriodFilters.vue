<template>
  <el-card class="period-filters">
    <template #header>
      <span class="font-semibold">Период анализа</span>
    </template>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Текущий период -->
      <div>
        <h4 class="text-sm font-medium text-gray-700 mb-3">Текущий период</h4>
        <div class="flex gap-2">
          <el-date-picker
            v-model="currentPeriod"
            type="daterange"
            range-separator="-"
            start-placeholder="Начало"
            end-placeholder="Конец"
            format="DD.MM.YYYY"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
          />
        </div>
        <div class="flex gap-2 mt-2">
          <el-button size="small" @click="setCurrentPeriod('30days')">30 дней</el-button>
          <el-button size="small" @click="setCurrentPeriod('month')">Этот месяц</el-button>
          <el-button size="small" @click="setCurrentPeriod('week')">Эта неделя</el-button>
        </div>
      </div>

      <!-- Прошлый период для сравнения -->
      <div>
        <h4 class="text-sm font-medium text-gray-700 mb-3">
          Период для сравнения
          <el-switch 
            v-model="compareEnabled" 
            class="ml-2"
            active-text="вкл"
            inactive-text="выкл"
          />
        </h4>
        <div v-if="compareEnabled" class="flex gap-2">
          <el-date-picker
            v-model="previousPeriod"
            type="daterange"
            range-separator="-"
            start-placeholder="Начало"
            end-placeholder="Конец"
            format="DD.MM.YYYY"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
          />
        </div>
        <div v-if="compareEnabled" class="flex gap-2 mt-2">
          <el-button size="small" @click="setPreviousPeriod('prev-month')">Пред. месяц</el-button>
          <el-button size="small" @click="setPreviousPeriod('prev-week')">Пред. неделя</el-button>
        </div>
      </div>
    </div>

    <div class="flex justify-end mt-4">
      <el-button 
        type="primary" 
        @click="applyFilters"
        :loading="loading"
        :disabled="!currentPeriod"
      >
        Применить
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref, watch } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update'])

const currentPeriod = ref([])
const previousPeriod = ref([])
const compareEnabled = ref(true)

const disabledDate = (time) => {
  return time.getTime() > Date.now()
}

const setCurrentPeriod = (type) => {
  const now = dayjs()
  switch (type) {
    case '30days':
      currentPeriod.value = [
        now.subtract(29, 'day').format('YYYY-MM-DD'),
        now.format('YYYY-MM-DD')
      ]
      break
    case 'month':
      currentPeriod.value = [
        now.startOf('month').format('YYYY-MM-DD'),
        now.format('YYYY-MM-DD')
      ]
      break
    case 'week':
      currentPeriod.value = [
        now.startOf('week').format('YYYY-MM-DD'),
        now.format('YYYY-MM-DD')
      ]
      break
  }
}

const setPreviousPeriod = (type) => {
  const start = dayjs(currentPeriod.value[0])
  const end = dayjs(currentPeriod.value[1])
  const duration = end.diff(start, 'day') + 1
  
  switch (type) {
    case 'prev-month':
      previousPeriod.value = [
        start.subtract(1, 'month').format('YYYY-MM-DD'),
        end.subtract(1, 'month').format('YYYY-MM-DD')
      ]
      break
    case 'prev-week':
      previousPeriod.value = [
        start.subtract(duration, 'day').format('YYYY-MM-DD'),
        end.subtract(duration, 'day').format('YYYY-MM-DD')
      ]
      break
  }
}

const applyFilters = () => {
  if (!currentPeriod.value || currentPeriod.value.length !== 2) {
    return
  }
  
  const filters = {
    current: {
      start: currentPeriod.value[0],
      end: currentPeriod.value[1]
    }
  }
  
  if (compareEnabled.value && previousPeriod.value && previousPeriod.value.length === 2) {
    filters.previous = {
      start: previousPeriod.value[0],
      end: previousPeriod.value[1]
    }
  }
  
  emit('update', filters)
}

// Автоматически устанавливаем последние 30 дней при монтировании
setCurrentPeriod('30days')
// Автоматически устанавливаем предыдущие 30 дней для сравнения
const now = dayjs()
previousPeriod.value = [
  now.subtract(59, 'day').format('YYYY-MM-DD'),
  now.subtract(30, 'day').format('YYYY-MM-DD')
]
// Автоматически применяем фильтры при монтировании
setTimeout(() => {
  applyFilters()
}, 100)
setPreviousPeriod('prev-month')

// Автоматически применяем фильтры при монтировании
setTimeout(() => applyFilters(), 100)
</script>
