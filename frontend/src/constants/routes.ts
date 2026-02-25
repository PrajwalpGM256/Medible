import type { NavItem } from '@/types'

export const ROUTES = {
  LANDING: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  MEDICATIONS: '/medications',
  INTERACTIONS: '/interactions',
  FOOD_DIARY: '/food-diary',
  PROFILE: '/profile',
  ADMIN: '/admin',
} as const

export const ROUTE_NAMES = {
  LANDING: 'landing',
  LOGIN: 'login',
  REGISTER: 'register',
  DASHBOARD: 'dashboard',
  MEDICATIONS: 'medications',
  INTERACTIONS: 'interactions',
  FOOD_DIARY: 'food-diary',
  PROFILE: 'profile',
  ADMIN: 'admin',
} as const

export const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', to: ROUTES.DASHBOARD, icon: 'LayoutDashboard', requiresAuth: true },
  { label: 'My Medications', to: ROUTES.MEDICATIONS, icon: 'Pill', requiresAuth: true },
  { label: 'Food & Nutrition', to: ROUTES.FOOD_DIARY, icon: 'BookOpen', requiresAuth: true },
  { label: 'Check Interactions', to: ROUTES.INTERACTIONS, icon: 'AlertTriangle', requiresAuth: true },
]

export const AUTH_NAV_ITEMS: NavItem[] = [
  { label: 'Login', to: ROUTES.LOGIN, icon: 'LogIn' },
  { label: 'Sign Up', to: ROUTES.REGISTER, icon: 'UserPlus' },
]