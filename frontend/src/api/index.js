import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  },
  paramsSerializer: {
    indexes: null // Убирает квадратные скобки для массивов
  }
})

// Interceptors для обработки ошибок
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  baseURL: '/api', // Экспортируем baseURL для прямого использования
  
  // Authors
  async getAuthors() {
    const response = await apiClient.get('/authors')
    return response.data
  },
  
  async createAuthor(data) {
    const response = await apiClient.post('/authors', data)
    return response.data
  },
  
  async getAuthor(id) {
    const response = await apiClient.get(`/authors/${id}`)
    return response.data
  },

  async updateAuthor(id, data) {
    const response = await apiClient.put(`/authors/${id}`, data)
    return response.data
  },

  async deleteAuthor(id) {
    const response = await apiClient.delete(`/authors/${id}`)
    return response.data
  },

  // Social Accounts
  async getSocialAccounts(authorId) {
    const response = await apiClient.get(`/social-accounts/authors/${authorId}`)
    return response.data
  },
  
  async createSocialAccount(data) {
    const response = await apiClient.post('/social-accounts', data)
    return response.data
  },
  
  async getSocialAccount(id) {
    const response = await apiClient.get(`/social-accounts/${id}`)
    return response.data
  },

  async updateSocialAccount(id, data) {
    const response = await apiClient.put(`/social-accounts/${id}`, data)
    return response.data
  },

  async deleteSocialAccount(id) {
    const response = await apiClient.delete(`/social-accounts/${id}`)
    return response.data
  },

  // Collect Data
  async collectTikTokData(socialAccountId, maxVideos = 100) {
    const response = await apiClient.post(`/collect/tiktok/${socialAccountId}`, {
      max_videos: maxVideos
    })
    return response.data
  },

  async collectYouTubeData(socialAccountId, maxVideos = 100) {
    const response = await apiClient.post(`/collect/youtube/${socialAccountId}`, {
      max_videos: maxVideos
    })
    return response.data
  },
  
  async getVideos(socialAccountId, params = {}) {
    const response = await apiClient.get(`/collect/videos/${socialAccountId}`, { params })
    return response.data
  },
  
  async getProfileSnapshots(socialAccountId, limit = 30) {
    const response = await apiClient.get(`/collect/profile-snapshots/${socialAccountId}`, {
      params: { limit }
    })
    return response.data
  },

  // Analytics
  async getAnalytics(socialAccountId, params = {}) {
    const response = await apiClient.get(`/analytics/${socialAccountId}`, { params })
    return response.data
  },

  async getComparativeAnalytics(platforms, period = '30d', customStart = null, customEnd = null, includePrevious = true) {
    // Создаем URLSearchParams для правильной сериализации массива
    const params = new URLSearchParams()
    
    // Добавляем каждую платформу отдельным параметром (platforms=tiktok&platforms=youtube)
    platforms.forEach(platform => {
      params.append('platforms', platform)
    })
    
    params.append('period', period)
    params.append('include_previous', includePrevious)
    
    if (customStart) params.append('custom_start', customStart)
    if (customEnd) params.append('custom_end', customEnd)
    
    const response = await apiClient.get('/analytics/comparative/platforms', { params })
    return response.data
  }
}
