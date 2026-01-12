<script setup lang="ts">
import { APP_NAME } from '@/constants'
import AppLogo from './AppLogo.vue'

const currentYear = new Date().getFullYear()
const links = [
  { label: 'Privacy', href: '#' },
  { label: 'Terms', href: '#' },
  { label: 'Contact', href: '#' },
]
</script>

<template>
  <footer class="border-t border-border bg-background">
    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div class="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
        <AppLogo size="sm" />
        <div class="flex gap-6">
          <a v-for="link in links" :key="link.label" :href="link.href" class="text-sm text-muted-foreground hover:text-foreground">{{ link.label }}</a>
        </div>
        <p class="text-sm text-muted-foreground">© {{ currentYear }} {{ APP_NAME }}</p>
      </div>
    </div>
  </footer>
</template>
