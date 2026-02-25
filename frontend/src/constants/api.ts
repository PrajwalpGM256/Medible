export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1'

export const ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    PROFILE: '/auth/me',
    UPDATE_PROFILE: '/auth/me',
    CHANGE_PASSWORD: '/auth/me/password',
    DELETE_ACCOUNT: '/auth/me',
    EXPORT_DATA: '/auth/me/export',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
  },
  ADMIN: {
    USERS: '/admin/users',
    USER: (id: number) => `/admin/users/${id}`,
    STATS: '/admin/stats',
  },
  DRUGS: {
    SEARCH: '/drugs/search',
    DETAILS: (name: string) => `/drugs/${encodeURIComponent(name)}`,
    INTERACTIONS: (name: string) => `/drugs/${encodeURIComponent(name)}/interactions`,
  },
  FOODS: {
    SEARCH: '/foods/search',
    DETAILS: (fdcId: string) => `/foods/${fdcId}`,
  },
  INTERACTIONS: {
    CHECK: '/interactions/check',
    CHECK_MULTIPLE: '/interactions/check-multiple',
    BY_DRUG: (name: string) => `/interactions/drug/${encodeURIComponent(name)}`,
    ALL: '/interactions',
  },
  USER_MEDICATIONS: {
    LIST: '/medications',
    ADD: '/medications',
    REMOVE: (id: number) => `/medications/${id}`,
    UPDATE: (id: number) => `/medications/${id}`,
  },
  FOOD_DIARY: {
    LIST: '/food-diary',
    TODAY: '/food-diary/today',
    ADD: '/food-diary',
    REMOVE: (id: number) => `/food-diary/${id}`,
    UPDATE: (id: number) => `/food-diary/${id}`,
    SUMMARY: '/food-diary/summary',
  },
  INTERACTION_HISTORY: {
    LIST: '/interaction-history',
    SAVE: '/interaction-history',
    DELETE: (id: number) => `/interaction-history/${id}`,
    CLEAR: '/interaction-history',
  },
} as const

export const API_CONFIG = {
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
  DEBOUNCE_MS: 300,
} as const
