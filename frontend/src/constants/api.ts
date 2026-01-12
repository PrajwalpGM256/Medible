export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1'

export const ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    PROFILE: '/auth/profile',
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
    BY_DRUG: (name: string) => `/interactions/drug/${encodeURIComponent(name)}`,
    ALL: '/interactions',
  },
  USER_MEDICATIONS: {
    LIST: '/medications',
    ADD: '/medications',
    REMOVE: (id: number) => `/medications/${id}`,
    UPDATE: (id: number) => `/medications/${id}`,
  },
} as const

export const API_CONFIG = {
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
  DEBOUNCE_MS: 300,
} as const
