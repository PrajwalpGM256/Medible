<script setup lang="ts">
import { Sun, Moon } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { useTheme } from '@/composables/useTheme'
const { theme, toggleTheme } = useTheme()
const icons = { light: Sun, dark: Moon }
</script>

<template>
  <Button variant="ghost" size="icon" class="h-10 w-10 group" @click="toggleTheme">
    <component 
      :is="icons[theme]" 
      class="h-5 w-5 transition-all duration-700 ease-in-out group-hover:rotate-[720deg] group-hover:scale-200" 
    />
  </Button>
</template>
