<script setup lang="ts">
import { Sun, Moon } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { useTheme } from '@/composables/useTheme'
const { theme, toggleTheme } = useTheme()
const icons = { light: Sun, dark: Moon }
</script>

<template>
  <Button variant="ghost" size="icon" class="h-10 w-10" @click="toggleTheme">
    <component :is="icons[theme]" class="h-5 w-5" />
  </Button>
</template>
