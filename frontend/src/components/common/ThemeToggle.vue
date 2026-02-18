<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Sun, Moon } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { useTheme } from '@/composables/useTheme'

const { theme, toggleTheme } = useTheme()
const icons = { light: Sun, dark: Moon }

const isMounted = ref(false)

onMounted(() => {
  setTimeout(() => {
    isMounted.value = true
  }, 50)
})
</script>

<template>
  <Button variant="ghost" size="icon" class="h-10 w-10 group" @click="toggleTheme">
    <div
      class="flex items-center justify-center"
      :class="[
        isMounted
          ? 'scale-100 rotate-0 opacity-100 transition-all duration-1000 ease-out'
          : 'scale-0 rotate-180 opacity-0'
      ]"
      style="transition-property: transform, opacity, rotate;"
    >
      <component
        :is="icons[theme]"
        class="h-5 w-5 transition-transform duration-500 group-hover:scale-120 group-hover:rotate-180"
      />
    </div>
  </Button>
</template>
