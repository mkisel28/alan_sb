<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <el-page-header @back="$router.push(`/authors/${authorId}`)" :title="author?.name || 'Автор'">
          <template #content>
            <div class="flex items-center justify-between w-full">
              <div class="flex items-center gap-4">
                <h1 class="text-2xl font-bold text-gray-900">{{ author?.name }}</h1>
                <el-tag v-if="socialAccount" type="success">{{ platformName }}</el-tag>
              </div>
              <el-button 
                type="primary" 
                :icon="DataAnalysis"
                @click="$router.push(`/authors/${authorId}/social/${socialAccountId}/analytics`)"
              >
                Аналитика
              </el-button>
            </div>
          </template>
        </el-page-header>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Stats Cards -->
      <div v-if="latestSnapshot" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white shadow-lg">
          <div class="text-sm opacity-90 mb-2">Подписчики</div>
          <el-tooltip :content="latestSnapshot.followers_count.toLocaleString()">
            <div class="text-3xl font-bold">{{ formatNumber(latestSnapshot.followers_count) }}</div>
          </el-tooltip>
        </div>
        
        <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white shadow-lg">
          <div class="text-sm opacity-90 mb-2">Всего лайков</div>
          <el-tooltip :content="latestSnapshot.total_likes?.toLocaleString() || '0'">
            <div class="text-3xl font-bold">{{ formatNumber(latestSnapshot.total_likes || 0) }}</div>
          </el-tooltip>
        </div>
        
        <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white shadow-lg">
          <div class="text-sm opacity-90 mb-2">Видео</div>
          <el-tooltip :content="latestSnapshot.total_posts?.toLocaleString() || '0'">
            <div class="text-3xl font-bold">{{ formatNumber(latestSnapshot.total_posts || 0) }}</div>
          </el-tooltip>
        </div>
        
        <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-6 text-white shadow-lg">
          <div class="text-sm opacity-90 mb-2">Всего просмотров</div>
          <el-tooltip :content="totalViews.toLocaleString()">
            <div class="text-3xl font-bold">{{ formatNumber(totalViews) }}</div>
          </el-tooltip>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Сортировка</label>
            <el-select v-model="filters.sortBy" @change="() => loadVideos(false)" class="w-full">
              <el-option label="По дате" value="date" />
              <el-option label="По просмотрам" value="views" />
              <el-option label="По лайкам" value="likes" />
              <el-option label="По комментариям" value="comments" />
              <el-option label="По шерам" value="shares" />
            </el-select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Порядок</label>
            <el-select v-model="filters.order" @change="() => loadVideos(false)" class="w-full">
              <el-option label="По убыванию" value="desc" />
              <el-option label="По возрастанию" value="asc" />
            </el-select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Период</label>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="-"
              start-placeholder="От"
              end-placeholder="До"
              @change="() => loadVideos(false)"
              class="w-full"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Кол-во на странице</label>
            <el-select v-model="filters.limit" @change="() => loadVideos(false)" class="w-full">
              <el-option :label="20" :value="20" />
              <el-option :label="50" :value="50" />
              <el-option :label="100" :value="100" />
              <el-option :label="200" :value="200" />
            </el-select>
          </div>
        </div>

        <div class="mt-4 flex justify-between items-center">
          <el-button @click="resetFilters" size="small">Сбросить фильтры</el-button>
          <span class="text-sm text-gray-600">Всего видео: {{ videos.length }}</span>
        </div>
      </div>

      <!-- Videos Grid -->
      <div v-loading="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div
          v-for="video in videos"
          :key="video.id"
          class="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-lg transition-shadow"
        >
          <!-- Video Preview with Play Button -->
          <div class="relative aspect-[9/16] bg-gray-200 group cursor-pointer" @click="playVideo(video)">
            <img
              v-if="video.cover_url"
              :src="getProxiedImageUrl(video.cover_url)"
              :alt="video.description"
              class="w-full h-full object-cover"
              @error="handleImageError"
            />
            <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all flex items-center justify-center">
              <div class="w-16 h-16 bg-white bg-opacity-90 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <el-icon :size="32" color="#409EFF">
                  <VideoPlay />
                </el-icon>
              </div>
            </div>
            <div class="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
              {{ formatDuration(video.duration_ms) }}
            </div>
          </div>

          <!-- Video Info -->
          <div class="p-4">
            <p class="text-sm text-gray-900 line-clamp-2 mb-3 min-h-[2.5rem]">
              {{ video.description || 'Без описания' }}
            </p>

            <!-- Stats -->
            <div class="grid grid-cols-2 gap-2 text-xs text-gray-600">
              <el-tooltip :content="`Просмотры: ${video.views_count.toLocaleString()}`">
                <div class="flex items-center gap-1">
                  <el-icon><View /></el-icon>
                  <span>{{ formatNumber(video.views_count) }}</span>
                </div>
              </el-tooltip>

              <el-tooltip :content="`Лайки: ${video.likes_count.toLocaleString()}`">
                <div class="flex items-center gap-1">
                  <el-icon><Star /></el-icon>
                  <span>{{ formatNumber(video.likes_count) }}</span>
                </div>
              </el-tooltip>

              <el-tooltip :content="`Комментарии: ${video.comments_count.toLocaleString()}`">
                <div class="flex items-center gap-1">
                  <el-icon><ChatDotRound /></el-icon>
                  <span>{{ formatNumber(video.comments_count) }}</span>
                </div>
              </el-tooltip>

              <el-tooltip :content="`Шеры: ${video.shares_count.toLocaleString()}`">
                <div class="flex items-center gap-1">
                  <el-icon><Share /></el-icon>
                  <span>{{ formatNumber(video.shares_count) }}</span>
                </div>
              </el-tooltip>
            </div>

            <div class="mt-3 pt-3 border-t text-xs text-gray-500">
              {{ formatDate(video.created_at_platform) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="videos.length >= filters.limit" class="mt-8 flex justify-center">
        <el-button @click="loadMore" :loading="loading">Загрузить еще</el-button>
      </div>
    </div>

    <!-- Video Player Dialog -->
    <el-dialog
      v-model="videoDialogVisible"
      title="Воспроизведение видео"
      width="90%"
      :close-on-click-modal="true"
    >
      <div v-if="currentVideo" class="aspect-[9/16] max-h-[80vh] mx-auto bg-black">
        <video
          :src="currentVideo.video_url"
          controls
          autoplay
          class="w-full h-full"
          @error="handleVideoError"
        >
          Ваш браузер не поддерживает воспроизведение видео.
        </video>
      </div>
      <template #footer>
        <div class="text-sm text-gray-600">
          <p class="mb-2">{{ currentVideo?.description }}</p>
          <a
            v-if="currentVideo?.share_url"
            :href="currentVideo.share_url"
            target="_blank"
            class="text-blue-600 hover:underline"
          >
            Открыть в TikTok
          </a>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View, Star, ChatDotRound, Share, VideoPlay, DataAnalysis } from '@element-plus/icons-vue'
import api from '../api'

const route = useRoute()
const router = useRouter()
const authorId = route.params.id
const socialAccountId = route.params.socialId

const author = ref(null)
const socialAccount = ref(null)
const latestSnapshot = ref(null)
const videos = ref([])
const allVideos = ref([]) // Все видео для подсчета общих просмотров
const loading = ref(false)
const videoDialogVisible = ref(false)
const currentVideo = ref(null)
const dateRange = ref(null)

const filters = ref({
  sortBy: 'date',
  order: 'desc',
  limit: 50,
  offset: 0
})

const platformName = computed(() => {
  const platforms = {
    tiktok: 'TikTok',
    instagram: 'Instagram',
    youtube: 'YouTube'
  }
  return platforms[socialAccount.value?.platform] || socialAccount.value?.platform
})

const totalViews = computed(() => {
  // Используем данные из snapshot для стабильности
  return allVideos.value.reduce((sum, v) => sum + (v.views_count || 0), 0)
})

const formatNumber = (num) => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatDuration = (ms) => {
  if (!ms) return '0:00'
  const seconds = Math.floor(ms / 1000)
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const getProxiedImageUrl = (url) => {
  // Используем прокси для изображений, чтобы избежать проблем с CORS и скачиванием
  if (!url) return ''
  // Можно использовать сервис прокси изображений или самописный endpoint
  return url
}

const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle"%3ENo Image%3C/text%3E%3C/svg%3E'
}

const playVideo = (video) => {
  if (!video.video_url) {
    ElMessage.warning('URL видео недоступен')
    return
  }
  currentVideo.value = video
  videoDialogVisible.value = true
}

const handleVideoError = () => {
  ElMessage.error('Не удалось загрузить видео. Попробуйте открыть в TikTok.')
}

const loadAuthor = async () => {
  try {
    const data = await api.getAuthor(authorId)
    author.value = data
  } catch (error) {
    ElMessage.error('Ошибка загрузки автора')
    console.error(error)
  }
}

const loadSocialAccount = async () => {
  try {
    const data = await api.getSocialAccount(socialAccountId)
    socialAccount.value = data
    await Promise.all([loadSnapshots(), loadAllVideos(), loadVideos()])
  } catch (error) {
    ElMessage.error('Ошибка загрузки соц. аккаунта')
    console.error(error)
  }
}

const loadAllVideos = async () => {
  if (!socialAccount.value) return
  try {
    // Загружаем все видео для подсчета общих метрик
    const data = await api.getVideos(socialAccount.value.id, { limit: 100, offset: 0 })
    allVideos.value = data
    console.log('Загружено всех видео:', data.length)
  } catch (error) {
    console.error('Ошибка загрузки всех видео:', error)
  }
}

const loadSnapshots = async () => {
  if (!socialAccount.value) return
  try {
    const data = await api.getProfileSnapshots(socialAccount.value.id, 1)
    if (data.length > 0) {
      latestSnapshot.value = data[0]
    }
  } catch (error) {
    console.error('Ошибка загрузки снимков профиля:', error)
  }
}

const loadVideos = async (append = false) => {
  if (!socialAccount.value) return
  
  loading.value = true
  
  if (!append) {
    filters.value.offset = 0
    videos.value = [] // Очищаем массив перед загрузкой
  }

  try {
    const params = {
      limit: filters.value.limit,
      offset: filters.value.offset,
      sort_by: filters.value.sortBy,
      order: filters.value.order
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.date_from = dateRange.value[0].toISOString()
      params.date_to = dateRange.value[1].toISOString()
    }

    const data = await api.getVideos(socialAccount.value.id, params)
    
    if (append) {
      videos.value = [...videos.value, ...data]
    } else {
      // Явно пересоздаем массив для триггера реактивности
      videos.value = [...data]
    }
  } catch (error) {
    ElMessage.error('Ошибка загрузки видео')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  filters.value.offset += filters.value.limit
  loadVideos(true)
}

const resetFilters = () => {
  filters.value = {
    sortBy: 'date',
    order: 'desc',
    limit: 50,
    offset: 0
  }
  dateRange.value = null
  loadVideos()
}

onMounted(async () => {
  await loadAuthor()
  await loadSocialAccount()
})
</script>
