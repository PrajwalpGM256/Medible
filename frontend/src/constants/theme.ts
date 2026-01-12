import type { Severity, Theme } from '@/types'

export const THEMES: Theme[] = ['light', 'dark', 'system']

export const THEME_STORAGE_KEY = 'medible-theme'

export const SEVERITY_CONFIG: Record<Severity, {
  label: string
  bgClass: string
  textClass: string
  borderClass: string
  icon: string
}> = {
  low: {
    label: 'Low Risk',
    bgClass: 'bg-emerald-50 dark:bg-emerald-950',
    textClass: 'text-emerald-700 dark:text-emerald-300',
    borderClass: 'border-emerald-200 dark:border-emerald-800',
    icon: 'CheckCircle',
  },
  moderate: {
    label: 'Moderate Risk',
    bgClass: 'bg-amber-50 dark:bg-amber-950',
    textClass: 'text-amber-700 dark:text-amber-300',
    borderClass: 'border-amber-200 dark:border-amber-800',
    icon: 'AlertCircle',
  },
  high: {
    label: 'High Risk',
    bgClass: 'bg-red-50 dark:bg-red-950',
    textClass: 'text-red-700 dark:text-red-300',
    borderClass: 'border-red-200 dark:border-red-800',
    icon: 'XCircle',
  },
}

export const FREQUENCY_OPTIONS = [
  { label: 'Once daily', value: 'once_daily' },
  { label: 'Twice daily', value: 'twice_daily' },
  { label: 'Three times daily', value: 'three_times_daily' },
  { label: 'Four times daily', value: 'four_times_daily' },
  { label: 'As needed', value: 'as_needed' },
  { label: 'Weekly', value: 'weekly' },
] as const