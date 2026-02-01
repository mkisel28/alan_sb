import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useAuthorsStore = defineStore('authors', () => {
  const authors = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchAuthors = async () => {
    loading.value = true
    error.value = null
    try {
      authors.value = await api.getAuthors()
    } catch (e) {
      error.value = e.message
      console.error('Error fetching authors:', e)
    } finally {
      loading.value = false
    }
  }

  const createAuthor = async (name) => {
    loading.value = true
    error.value = null
    try {
      const newAuthor = await api.createAuthor({ name })
      authors.value.push(newAuthor)
      return newAuthor
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const getAuthorById = (id) => {
    return authors.value.find(a => a.id === id)
  }

  return {
    authors,
    loading,
    error,
    fetchAuthors,
    createAuthor,
    getAuthorById
  }
})
