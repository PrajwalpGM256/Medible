<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import { useAuthStore } from '@/stores/auth'
import { Toaster } from '@/components/ui/sonner'

const { isDark } = useTheme()
const auth = useAuthStore()
const router = useRouter()
const isValidating = ref(true)

onMounted(async () => {
  // Always validate token on app startup BEFORE showing UI
  // If token is invalid (e.g., server restarted), user will be logged out
  if (auth.token) {
    try {
      const isValid = await auth.validateSession()
      if (!isValid) {
        router.push('/login')
      }
    } catch {
      auth.logout()
      router.push('/login')
    }
  }
  isValidating.value = false
})
</script>

<template>
  <!-- Show loading until auth validation is complete -->
  <div v-if="isValidating" class="flex min-h-screen items-center justify-center bg-background">
    <div class="flex flex-col items-center gap-3">
      <div class="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
      <p class="text-sm text-muted-foreground">Loading...</p>
    </div>
  </div>
  <div v-else class="min-h-screen bg-background text-foreground">
    <RouterView />
    <Toaster :theme="isDark ? 'dark' : 'light'" position="top-right" />
  </div>
</template>