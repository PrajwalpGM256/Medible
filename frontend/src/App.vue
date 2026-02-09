<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import { useAuthStore } from '@/stores/auth'
import { Toaster } from '@/components/ui/sonner'

const { isDark } = useTheme()
const auth = useAuthStore()
const router = useRouter()

onMounted(async () => {
  // Always validate token on app startup
  // If token is invalid (e.g., server restarted), user will be logged out
  if (auth.token) {
    const isValid = await auth.validateSession()
    if (!isValid) {
      // Token was invalid, redirect to login
      router.push('/login')
    }
  }
})
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <RouterView />
    <Toaster :theme="isDark ? 'dark' : 'light'" position="top-right" />
  </div>
</template>