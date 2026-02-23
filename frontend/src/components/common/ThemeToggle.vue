<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Sun, Moon } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { useTheme } from '@/composables/useTheme'

const { theme, toggleTheme } = useTheme()
const icons: Record<string, typeof Sun> = { light: Sun, dark: Moon }

const isMounted = ref(false)

onMounted(() => {
  setTimeout(() => {
    isMounted.value = true
  }, 50)
})
</script>

<template>
  <Button variant="ghost" size="icon" class="h-10 w-10 group" @click="toggleTheme">
    <component 
      :is="icons[theme]" 
      class="h-5 w-5 transition-all duration-700 ease-in-out group-hover:rotate-[720deg] group-hover:scale-200" 
    />
  </Button>
</template>
