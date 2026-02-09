import { ref, watch } from 'vue'
import { useStorage } from '@vueuse/core'
import type { Theme } from '@/types'
import { THEME_STORAGE_KEY } from '@/constants'

export function useTheme() {
  const storedTheme = useStorage<Theme>(THEME_STORAGE_KEY, 'light')
  const theme = ref<Theme>(storedTheme.value)

  const isDark = ref(false)

  function updateDarkMode() {
    isDark.value = theme.value === 'dark'
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    storedTheme.value = newTheme
    updateDarkMode()
  }

  function toggleTheme() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  // Initialize immediately (not just on mount)
  updateDarkMode()

  return {
    theme,
    isDark,
    setTheme,
    toggleTheme,
    themes: ['light', 'dark'],
  }
}