import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User, LoginForm, LoginResponse } from '@/services/types'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isAuthenticated = ref<boolean>(!!token.value)

  const login = async (loginForm: LoginForm): Promise<void> => {
    try {
      const response: LoginResponse = await api.post('/auth/login', loginForm)
      
      token.value = response.access_token
      user.value = response.user
      isAuthenticated.value = true
      
      localStorage.setItem('token', response.access_token)
    } catch (error) {
      throw error
    }
  }

  const logout = (): void => {
    token.value = null
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
  }

  const getCurrentUser = async (): Promise<void> => {
    try {
      const response: User = await api.get('/auth/me')
      user.value = response
    } catch (error) {
      logout()
      throw error
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    getCurrentUser
  }
})