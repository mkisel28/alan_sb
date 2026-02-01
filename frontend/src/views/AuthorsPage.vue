<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <el-card class="shadow-sm">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="text-xl font-bold text-gray-900">Список авторов</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            Добавить автора
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="authorsStore.loading"
        :data="authorsStore.authors"
        style="width: 100%"
        @row-click="handleRowClick"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="Имя" />
        <el-table-column label="Соц. сети" width="120">
          <template #default="{ row }">
            <el-tag>{{ getAccountsCount(row.id) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Дата создания" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="Действия" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click.stop="addSocialAccount(row.id)"
            >
              <el-icon><Plus /></el-icon>
              Добавить соцсеть
            </el-button>
            <el-dropdown @command="(cmd) => handleAuthorAction(cmd, row)" trigger="click">
              <el-button size="small" @click.stop>
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="view">Подробнее</el-dropdown-item>
                  <el-dropdown-item command="edit">Изменить</el-dropdown-item>
                  <el-dropdown-item command="delete" style="color: #f56c6c;">Удалить</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create Author Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      title="Добавить автора"
      width="500px"
    >
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="Имя">
          <el-input v-model="createForm.name" placeholder="Введите имя автора" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">Отмена</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">
          Создать
        </el-button>
      </template>
    </el-dialog>

    <!-- Edit Author Dialog -->
    <el-dialog
      v-model="showEditDialog"
      title="Изменить автора"
      width="500px"
    >
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="Имя">
          <el-input v-model="editForm.name" placeholder="Введите имя автора" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">Отмена</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="creating">
          Сохранить
        </el-button>
      </template>
    </el-dialog>

    <!-- Add Social Account Dialog -->
    <el-dialog
      v-model="showSocialDialog"
      title="Добавить социальную сеть"
      width="600px"
    >
      <el-form :model="socialForm" label-width="150px">
        <el-form-item label="Платформа">
          <el-select v-model="socialForm.platform" placeholder="Выберите платформу">
            <el-option label="TikTok" value="tiktok" />
            <el-option label="Instagram" value="instagram" disabled />
            <el-option label="YouTube" value="youtube" />
            <el-option label="YouTube Shorts" value="youtube_shorts" />
          </el-select>
        </el-form-item>

        <el-form-item label="User ID">
          <el-input
            v-model="socialForm.platform_user_id"
            placeholder="6868974846787077121"
          />
        </el-form-item>

        <el-form-item label="Username">
          <el-input
            v-model="socialForm.username"
            placeholder="ksenia_buglak"
          />
        </el-form-item>

        <el-form-item label="URL профиля">
          <el-input
            v-model="socialForm.profile_url"
            placeholder="https://www.tiktok.com/@username"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showSocialDialog = false">Отмена</el-button>
        <el-button type="primary" @click="handleCreateSocial" :loading="creating">
          Добавить
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, MoreFilled } from '@element-plus/icons-vue'
import { useAuthorsStore } from '@/stores/authors'
import { useSocialAccountsStore } from '@/stores/socialAccounts'
import dayjs from 'dayjs'
import api from '@/api'

const router = useRouter()
const authorsStore = useAuthorsStore()
const socialAccountsStore = useSocialAccountsStore()

const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showSocialDialog = ref(false)
const creating = ref(false)

const createForm = ref({
  name: ''
})

const editForm = ref({
  id: null,
  name: ''
})

const socialForm = ref({
  author_id: null,
  platform: 'tiktok',
  platform_user_id: '',
  username: '',
  profile_url: ''
})

const accountsCounts = ref({})

const handleCreate = async () => {
  if (!createForm.value.name) {
    ElMessage.warning('Введите имя автора')
    return
  }

  creating.value = true
  try {
    await authorsStore.createAuthor(createForm.value.name)
    ElMessage.success('Автор создан')
    showCreateDialog.value = false
    createForm.value.name = ''
  } catch (error) {
    ElMessage.error('Ошибка при создании автора')
  } finally {
    creating.value = false
  }
}

const editAuthor = (author) => {
  editForm.value.id = author.id
  editForm.value.name = author.name
  showEditDialog.value = true
}

const handleUpdate = async () => {
  if (!editForm.value.name) {
    ElMessage.warning('Введите имя автора')
    return
  }

  creating.value = true
  try {
    await api.updateAuthor(editForm.value.id, { name: editForm.value.name })
    await authorsStore.fetchAuthors()
    ElMessage.success('Автор обновлен')
    showEditDialog.value = false
  } catch (error) {
    ElMessage.error('Ошибка при обновлении автора')
  } finally {
    creating.value = false
  }
}

const confirmDeleteAuthor = (author) => {
  ElMessageBox.confirm(
    `Вы уверены, что хотите удалить автора "${author.name}"? Это действие удалит все связанные социальные аккаунты, видео и статистику.`,
    'Подтверждение удаления',
    {
      confirmButtonText: 'Удалить',
      cancelButtonText: 'Отмена',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    }
  ).then(async () => {
    try {
      await api.deleteAuthor(author.id)
      await authorsStore.fetchAuthors()
      ElMessage.success('Автор удален')
    } catch (error) {
      ElMessage.error('Ошибка при удалении автора')
    }
  }).catch(() => {
    // Пользователь отменил
  })
}

const handleAuthorAction = (command, author) => {
  if (command === 'view') {
    viewAuthor(author.id)
  } else if (command === 'edit') {
    editAuthor(author)
  } else if (command === 'delete') {
    confirmDeleteAuthor(author)
  }
}

const addSocialAccount = (authorId) => {
  socialForm.value.author_id = authorId
  socialForm.value.platform = 'tiktok'
  socialForm.value.platform_user_id = ''
  socialForm.value.username = ''
  socialForm.value.profile_url = ''
  showSocialDialog.value = true
}

const handleCreateSocial = async () => {
  if (!socialForm.value.platform_user_id) {
    ElMessage.warning('Введите User ID')
    return
  }

  creating.value = true
  try {
    await socialAccountsStore.createSocialAccount(socialForm.value)
    ElMessage.success('Социальная сеть добавлена')
    showSocialDialog.value = false
    loadAccountsCounts()
  } catch (error) {
    ElMessage.error('Ошибка при добавлении социальной сети')
  } finally {
    creating.value = false
  }
}

const viewAuthor = (id) => {
  router.push(`/authors/${id}`)
}

const handleRowClick = (row) => {
  viewAuthor(row.id)
}

const getAccountsCount = (authorId) => {
  return accountsCounts.value[authorId] || 0
}

const loadAccountsCounts = async () => {
  for (const author of authorsStore.authors) {
    await socialAccountsStore.fetchSocialAccounts(author.id)
    accountsCounts.value[author.id] = socialAccountsStore.socialAccounts.length
  }
}

const formatDate = (date) => {
  return dayjs(date).format('DD.MM.YYYY HH:mm')
}

onMounted(async () => {
  await authorsStore.fetchAuthors()
  loadAccountsCounts()
})
</script>

<style scoped>
.el-table :deep(.el-table__row) {
  cursor: pointer;
}

.el-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
