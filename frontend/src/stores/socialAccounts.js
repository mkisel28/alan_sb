import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useSocialAccountsStore = defineStore('socialAccounts', () => {
  const socialAccounts = ref([])
  const videos = ref([])
  const profileSnapshots = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchSocialAccounts = async (authorId) => {
    loading.value = true
    error.value = null
    try {
      socialAccounts.value = await api.getSocialAccounts(authorId)
    } catch (e) {
      error.value = e.message
      console.error('Error fetching social accounts:', e)
    } finally {
      loading.value = false
    }
  }

  const createSocialAccount = async (data) => {
    loading.value = true
    error.value = null
    try {
      const newAccount = await api.createSocialAccount(data)
      socialAccounts.value.push(newAccount)
      return newAccount
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const collectTikTokData = async (socialAccountId, maxVideos = 100) => {
    loading.value = true
    error.value = null
    try {
      return await api.collectTikTokData(socialAccountId, maxVideos)
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchVideos = async (socialAccountId, params = {}) => {
    loading.value = true
    error.value = null
    try {
      videos.value = await api.getVideos(socialAccountId, params)
    } catch (e) {
      error.value = e.message
      console.error('Error fetching videos:', e)
    } finally {
      loading.value = false
    }
  }

  const fetchProfileSnapshots = async (socialAccountId, limit = 30) => {
    loading.value = true
    error.value = null
    try {
      profileSnapshots.value = await api.getProfileSnapshots(socialAccountId, limit)
    } catch (e) {
      error.value = e.message
      console.error('Error fetching profile snapshots:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    socialAccounts,
    videos,
    profileSnapshots,
    loading,
    error,
    fetchSocialAccounts,
    createSocialAccount,
    collectTikTokData,
    fetchVideos,
    fetchProfileSnapshots
  }
})
