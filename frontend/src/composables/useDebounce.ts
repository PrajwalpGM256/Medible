import { ref, watch } from 'vue'
import type { Ref } from 'vue'
import { API_CONFIG } from '@/constants'

export function useDebounce<T>(
  value: Ref<T>,
  delay: number = API_CONFIG.DEBOUNCE_MS
): Ref<T> {
  const debouncedValue = ref(value.value) as Ref<T>
  let timeout: ReturnType<typeof setTimeout>

  watch(value, (newValue) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => {
      debouncedValue.value = newValue
    }, delay)
  })

  return debouncedValue
}

export function useDebouncedFn<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = API_CONFIG.DEBOUNCE_MS
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout>

  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => fn(...args), delay)
  }
}