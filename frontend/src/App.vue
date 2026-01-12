<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import { useAuthStore } from '@/stores/auth'
import { Toaster } from '@/components/ui/sonner'

const { isDark } = useTheme()
const auth = useAuthStore()

onMounted(() => {
  if (auth.token) auth.fetchProfile()
})
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <RouterView />
    <Toaster :theme="isDark ? 'dark' : 'light'" position="top-right" />
  </div>
</template>