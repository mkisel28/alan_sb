import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCollectionProgressStore = defineStore('collectionProgress', () => {
  const isCollecting = ref(false)
  const total = ref(0)
  const completed = ref(0)
  const failed = ref(0)
  const currentAccount = ref(null)
  const errors = ref([])

  const progress = computed(() => {
    if (total.value === 0) return 0
    return Math.round((completed.value / total.value) * 100)
  })

  const startCollection = (totalAccounts) => {
    isCollecting.value = true
    total.value = totalAccounts
    completed.value = 0
    failed.value = 0
    currentAccount.value = null
    errors.value = []
  }

  const updateProgress = (accountName) => {
    currentAccount.value = accountName
  }

  const markCompleted = () => {
    completed.value++
  }

  const markFailed = (accountName, error) => {
    completed.value++
    failed.value++
    errors.value.push({ account: accountName, error })
  }

  const finishCollection = () => {
    isCollecting.value = false
    currentAccount.value = null
  }

  const reset = () => {
    isCollecting.value = false
    total.value = 0
    completed.value = 0
    failed.value = 0
    currentAccount.value = null
    errors.value = []
  }

  return {
    isCollecting,
    total,
    completed,
    failed,
    currentAccount,
    errors,
    progress,
    startCollection,
    updateProgress,
    markCompleted,
    markFailed,
    finishCollection,
    reset
  }
})
