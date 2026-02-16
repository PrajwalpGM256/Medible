<script setup lang="ts">
import { ArrowUp } from 'lucide-vue-next'
import { APP_NAME } from '@/constants'
import AppLogo from './AppLogo.vue'

const currentYear = new Date().getFullYear()

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <footer class="border-t border-border bg-background/80 backdrop-blur-md">
    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div class="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
        <AppLogo size="sm" />
        
        <button 
          @click="scrollToTop"
          class="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-primary transition-colors cursor-pointer group"
        >
          <span>Back to top</span>
          <ArrowUp class="h-4 w-4 group-hover:-translate-y-1 transition-transform" />
        </button>

        <p class="text-sm text-muted-foreground">© {{ currentYear }} {{ APP_NAME }}</p>
      </div>
    </div>
  </footer>
</template>
