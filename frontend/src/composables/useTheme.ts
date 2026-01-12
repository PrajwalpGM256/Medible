import { ref, watch } from 'vue'
import { usePreferredDark, useStorage } from '@vueuse/core'
import type { Theme } from '@/types'
import { THEME_STORAGE_KEY, THEMES } from '@/constants'

export function useTheme() {
  const prefersDark = usePreferredDark()
  const storedTheme = useStorage<Theme>(THEME_STORAGE_KEY, 'system')
  const theme = ref<Theme>(storedTheme.value)

  const isDark = ref(false)

  function updateDarkMode() {
    if (theme.value === 'system') {
      isDark.value = prefersDark.value
    } else {
      isDark.value = theme.value === 'dark'
    }
    
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    storedTheme.value = newTheme
    updateDarkMode()
  }

  function toggleTheme() {
    const currentIndex = THEMES.indexOf(theme.value)
    const nextIndex = (currentIndex + 1) % THEMES.length
    setTheme(THEMES[nextIndex])
  }

  // Watch for system preference changes
  watch(prefersDark, updateDarkMode)

  // Initialize immediately (not just on mount)
  updateDarkMode()

  return {
    theme,
    isDark,
    setTheme,
    toggleTheme,
    themes: THEMES,
  }
}