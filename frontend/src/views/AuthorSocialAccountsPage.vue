<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <el-page-header @back="$router.push('/authors')" :title="author?.name || 'Автор'">
          <template #content>
            <div class="flex items-center gap-4">
              <h1 class="text-2xl font-bold text-gray-900">{{ author?.name }}</h1>
            </div>
          </template>
        </el-page-header>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-loading="loading">
        <!-- Если нет соцсетей -->
        <el-empty v-if="!loading && socialAccounts.length === 0" description="У автора нет добавленных социальных сетей">
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>
            Добавить соцсеть
          </el-button>
        </el-empty>

        <!-- Список соцсетей -->
        <div v-else>
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold text-gray-900">Социальные сети</h2>
            <el-button type="primary" @click="showAddDialog = true">
              <el-icon><Plus /></el-icon>
              Добавить соцсеть
            </el-button>
          </div>

          <div class="grid gap-6" style="grid-template-columns: repeat(auto-fit, minmax(320px, 1fr))">
            <div
              v-for="account in socialAccounts"
              :key="account.id"
              class="bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow overflow-hidden"
            >
              <!-- Platform Icon/Header -->
              <div :class="getPlatformHeaderClass(account.platform)" class="p-6">
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center gap-3">
                    <div class="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                      <el-icon :size="24">
                        <component :is="getPlatformIcon(account.platform)" />
                      </el-icon>
                    </div>
                    <div class="text-white">
                      <div class="text-sm opacity-90">{{ getPlatformName(account.platform) }}</div>
                      <div class="text-lg font-bold">@{{ account.username || 'Не указан' }}</div>
                    </div>
                  </div>
                  <el-tag :type="account.is_active ? 'success' : 'info'" size="small" effect="light">
                    {{ account.is_active ? 'Активен' : 'Неактивен' }}
                  </el-tag>
                </div>

                <!-- Avatar & Stats -->
                <div v-if="getSnapshot(account.id)" class="flex items-center gap-4">
                  <el-avatar 
                    v-if="getSnapshot(account.id).avatar_url" 
                    :src="getSnapshot(account.id).avatar_url"
                    :size="64"
                    class="border-2 border-white border-opacity-50"
                  />
                  <div class="flex-1 grid grid-cols-2 gap-2 text-white text-sm">
                    <div>
                      <div class="opacity-75">Подписчики</div>
                      <div class="text-lg font-bold">{{ formatNumber(getSnapshot(account.id).followers_count) }}</div>
                    </div>
                    <div>
                      <div class="opacity-75">Видео</div>
                      <div class="text-lg font-bold">{{ formatNumber(getSnapshot(account.id).total_posts) }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Account Info -->
              <div class="p-6">
                <!-- Stats Grid -->
                <div v-if="getSnapshot(account.id)" class="grid grid-cols-2 gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
                  <div class="text-center">
                    <div class="text-2xl font-bold text-purple-600">
                      {{ formatNumber(getSnapshot(account.id).total_likes) }}
                    </div>
                    <div class="text-xs text-gray-600 mt-1">Всего лайков</div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-bold text-blue-600">
                      {{ formatNumber(getSnapshot(account.id).following_count) }}
                    </div>
                    <div class="text-xs text-gray-600 mt-1">Подписки</div>
                  </div>
                </div>

                <div class="space-y-3">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-600">User ID:</span>
                    <span class="font-mono text-gray-900 text-xs">{{ account.platform_user_id }}</span>
                  </div>
                  
                  <div v-if="account.profile_url" class="flex items-center justify-between text-sm">
                    <span class="text-gray-600">Профиль:</span>
                    <a 
                      :href="account.profile_url" 
                      target="_blank" 
                      class="text-blue-600 hover:underline"
                      @click.stop
                    >
                      Открыть
                    </a>
                  </div>

                  <div v-if="getSnapshot(account.id)" class="flex items-center justify-between text-sm">
                    <span class="text-gray-600">Обновлено:</span>
                    <span class="text-gray-900">{{ formatDate(getSnapshot(account.id).snapshot_date) }}</span>
                  </div>

                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-600">Добавлен:</span>
                    <span class="text-gray-900">{{ formatDate(account.created_at) }}</span>
                  </div>
                </div>

                <!-- Actions -->
                <div class="mt-4 pt-4 border-t flex gap-2">
                  <el-button 
                    type="primary" 
                    class="flex-1"
                    @click="openSocialAccount(account.id)"
                  >
                    <el-icon><View /></el-icon>
                    Открыть
                  </el-button>
                  <el-button 
                    type="success" 
                  
                    @click.stop="collectData(account.id)"
                    :loading="loading"
                  >
                    <el-icon><Download /></el-icon>
                  </el-button>
                  <el-dropdown @command="(cmd) => handleAccountAction(cmd, account)">
                    <el-button>
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="edit">Изменить</el-dropdown-item>
                        <el-dropdown-item command="delete" style="color: #f56c6c;">Удалить</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Social Account Dialog -->
    <el-dialog
      v-model="showAddDialog"
      title="Добавить социальную сеть"
      width="600px"
    >
      <el-form :model="socialForm" label-width="150px">
        <el-form-item label="Платформа">
          <el-select v-model="socialForm.platform" placeholder="Выберите платформу" class="w-full">
            <el-option label="TikTok" value="tiktok" />
            <el-option label="Instagram" value="instagram" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="YouTube" value="youtube" />
            <el-option label="YouTube Shorts" value="youtube_shorts" />
          </el-select>
        </el-form-item>

        <el-form-item label="User ID">
          <el-input
            v-model="socialForm.platform_user_id"
            :placeholder="
              socialForm.platform === 'youtube' || socialForm.platform === 'youtube_shorts' 
                ? 'UCxxxxxxxxxxxxxxxxxxxxxx (Channel ID)' 
                : socialForm.platform === 'instagram'
                ? 'ph_maxsel (username/handle)'
                : socialForm.platform === 'telegram'
                ? '@channelname или ID канала'
                : '6868974846787077121'
            "
          />
        </el-form-item>

        <el-form-item label="Username">
          <el-input
            v-model="socialForm.username"
            :placeholder="
              socialForm.platform === 'youtube' || socialForm.platform === 'youtube_shorts' 
                ? '@channelname или Channel Name' 
                : socialForm.platform === 'instagram'
                ? 'ph_maxsel'
                : socialForm.platform === 'telegram'
                ? '@channelname'
                : 'ksenia_buglak'
            "
          />
        </el-form-item>

        <el-form-item label="URL профиля">
          <el-input
            v-model="socialForm.profile_url"
            :placeholder="
              socialForm.platform === 'youtube' || socialForm.platform === 'youtube_shorts' 
                ? 'https://www.youtube.com/@channelname' 
                : socialForm.platform === 'instagram'
                ? 'https://www.instagram.com/ph_maxsel/'
                : socialForm.platform === 'telegram'
                ? 'https://t.me/channelname'
                : 'https://www.tiktok.com/@username'
            "
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddDialog = false">Отмена</el-button>
        <el-button type="primary" @click="handleAddSocial" :loading="creating">
          Добавить
        </el-button>
      </template>
    </el-dialog>

    <!-- Edit Social Account Dialog -->
    <el-dialog
      v-model="showEditDialog"
      title="Изменить социальную сеть"
      width="600px"
    >
      <el-form :model="editForm" label-width="150px">
        <el-form-item label="Платформа">
          <el-input :value="getPlatformName(editForm.platform)" disabled />
        </el-form-item>

        <el-form-item label="User ID">
          <el-input v-model="editForm.platform_user_id" disabled />
        </el-form-item>

        <el-form-item label="Username">
          <el-input
            v-model="editForm.username"
            placeholder="ksenia_buglak"
          />
        </el-form-item>

        <el-form-item label="URL профиля">
          <el-input
            v-model="editForm.profile_url"
            placeholder="https://www.tiktok.com/@username"
          />
        </el-form-item>

        <el-form-item label="Статус">
          <el-switch
            v-model="editForm.is_active"
            active-text="Активен"
            inactive-text="Неактивен"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">Отмена</el-button>
        <el-button type="primary" @click="handleEditSocial" :loading="creating">
          Сохранить
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowRight, View, Download, VideoCamera, MoreFilled } from '@element-plus/icons-vue'
import api from '../api'

const route = useRoute()
const router = useRouter()
const authorId = route.params.id

const author = ref(null)
const socialAccounts = ref([])
const snapshots = ref({}) // Словарь snapshots по social_account_id
const loading = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const creating = ref(false)

const socialForm = ref({
  author_id: null,
  platform: 'tiktok',
  platform_user_id: '',
  username: '',
  profile_url: ''
})

const editForm = ref({
  id: null,
  platform: '',
  platform_user_id: '',
  username: '',
  profile_url: '',
  is_active: true
})

const getPlatformName = (platform) => {
  const platforms = {
    tiktok: 'TikTok',
    youtube: 'YouTube',
    youtube_shorts: 'YouTube Shorts',
    instagram: 'Instagram',
    facebook: 'Facebook',
    twitter: 'Twitter/X',
    telegram: 'Telegram'
  }
  return platforms[platform] || platform
}

const getPlatformIcon = (platform) => {
  // Используем VideoCamera как placeholder для всех платформ
  return VideoCamera
}

const getPlatformHeaderClass = (platform) => {
  const classes = {
    tiktok: 'bg-gradient-to-br from-pink-500 to-purple-600',
    youtube: 'bg-gradient-to-br from-red-500 to-red-700',
    youtube_shorts: 'bg-gradient-to-br from-red-600 to-pink-600',
    instagram: 'bg-gradient-to-br from-purple-500 to-pink-600',
    facebook: 'bg-gradient-to-br from-blue-500 to-blue-700',
    twitter: 'bg-gradient-to-br from-sky-400 to-blue-500',
    telegram: 'bg-gradient-to-br from-blue-400 to-blue-600'
  }
  return classes[platform] || 'bg-gradient-to-br from-gray-500 to-gray-700'
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
   })
}


const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

const getSnapshot = (socialAccountId) => {
  return snapshots.value[socialAccountId] || null
} 

const openSocialAccount = (socialAccountId) => {
  router.push(`/authors/${authorId}/social/${socialAccountId}`)
}

const collectData = async (socialAccountId) => {
  const account = socialAccounts.value.find(a => a.id === socialAccountId)
  if (!account) return

  try {
    loading.value = true
    
    // Определяем endpoint в зависимости от платформы
    let endpoint = null
    if (account.platform === 'tiktok') {
      endpoint = api.collectTikTokData(socialAccountId, null, null)
    } else if (account.platform === 'youtube' || account.platform === 'youtube_shorts') {
      endpoint = api.collectYouTubeData(socialAccountId, null, null)
    } else if (account.platform === 'instagram') {
      endpoint = api.collectInstagramData(socialAccountId, null, null)
    } else if (account.platform === 'telegram') {
      endpoint = api.collectTelegramData(socialAccountId, null, null)
    } else {
      ElMessage.warning(`Сбор данных для ${account.platform} пока не поддерживается`)
      return
    }

    await endpoint
    ElMessage.success('Сбор данных начат')
    
    // Обновляем snapshot после сбора
    await loadSnapshot(socialAccountId)
  } catch (error) {
    ElMessage.error('Ошибка при сборе данных')
    console.error(error)
  } finally {
    loading.value = false
  }
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

const loadSnapshot = async (socialAccountId) => {
  try {
    const data = await api.getProfileSnapshots(socialAccountId, 1)
    if (data.length > 0) {
      snapshots.value[socialAccountId] = data[0]
    }
  } catch (error) {
    console.error(`Ошибка загрузки snapshot для аккаунта ${socialAccountId}:`, error)
}}

const loadSocialAccounts = async () => {
  loading.value = true
  try {
    const data = await api.getSocialAccounts(authorId)
    socialAccounts.value = data
    
    // Загружаем snapshots для каждой соцсети
    await Promise.all(
      data.map(account => loadSnapshot(account.id))
    )
  } catch (error) {
    ElMessage.error('Ошибка загрузки соц. аккаунтов')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleAddSocial = async () => {
  if (!socialForm.value.platform_user_id) {
    ElMessage.warning('Введите User ID')
    return
  }

  socialForm.value.author_id = parseInt(authorId)
  creating.value = true
  
  try {
    await api.createSocialAccount(socialForm.value)
    ElMessage.success('Социальная сеть добавлена')
    showAddDialog.value = false
    socialForm.value = {
      author_id: null,
      platform: 'tiktok',
      platform_user_id: '',
      username: '',
      profile_url: ''
    }
    await loadSocialAccounts()
  } catch (error) {
    ElMessage.error('Ошибка при добавлении социальной сети')
    console.error(error)
  } finally {
    creating.value = false
  }
}

const handleAccountAction = (command, account) => {
  if (command === 'edit') {
    editSocialAccount(account)
  } else if (command === 'delete') {
    confirmDeleteSocialAccount(account)
  }
}

const editSocialAccount = (account) => {
  editForm.value = {
    id: account.id,
    platform: account.platform,
    platform_user_id: account.platform_user_id,
    username: account.username || '',
    profile_url: account.profile_url || '',
    is_active: account.is_active
  }
  showEditDialog.value = true
}

const handleEditSocial = async () => {
  creating.value = true
  try {
    await api.updateSocialAccount(editForm.value.id, {
      username: editForm.value.username,
      profile_url: editForm.value.profile_url,
      is_active: editForm.value.is_active
    })
    ElMessage.success('Социальный аккаунт обновлен')
    showEditDialog.value = false
    await loadSocialAccounts()
  } catch (error) {
    ElMessage.error('Ошибка при обновлении')
    console.error(error)
  } finally {
    creating.value = false
  }
}

const confirmDeleteSocialAccount = (account) => {
  ElMessageBox.confirm(
    `Вы уверены, что хотите удалить социальный аккаунт @${account.username || account.platform_user_id}? Это действие удалит все связанные видео и статистику.`,
    'Подтверждение удаления',
    {
      confirmButtonText: 'Удалить',
      cancelButtonText: 'Отмена',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    }
  ).then(async () => {
    try {
      await api.deleteSocialAccount(account.id)
      ElMessage.success('Социальный аккаунт удален')
      await loadSocialAccounts()
    } catch (error) {
      ElMessage.error('Ошибка при удалении')
      console.error(error)
    }
  }).catch(() => {
    // Пользователь отменил
  })
}

onMounted(async () => {
  await loadAuthor()
  await loadSocialAccounts()
})
</script>
