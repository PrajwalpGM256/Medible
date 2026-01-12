import type { NavItem } from '@/types'

export const ROUTES = {
  LANDING: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  MEDICATIONS: '/medications',
  INTERACTIONS: '/interactions',
  CHECK: '/check',
  PROFILE: '/profile',
} as const

export const ROUTE_NAMES = {
  LANDING: 'landing',
  LOGIN: 'login',
  REGISTER: 'register',
  DASHBOARD: 'dashboard',
  MEDICATIONS: 'medications',
  INTERACTIONS: 'interactions',
  CHECK: 'check',
  PROFILE: 'profile',
} as const

export const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', to: ROUTES.DASHBOARD, icon: 'LayoutDashboard', requiresAuth: true },
  { label: 'My Medications', to: ROUTES.MEDICATIONS, icon: 'Pill', requiresAuth: true },
  { label: 'Interactions', to: ROUTES.INTERACTIONS, icon: 'AlertTriangle', requiresAuth: true },
  { label: 'Food Check', to: ROUTES.CHECK, icon: 'Search', requiresAuth: true },
]

export const AUTH_NAV_ITEMS: NavItem[] = [
  { label: 'Login', to: ROUTES.LOGIN, icon: 'LogIn' },
  { label: 'Sign Up', to: ROUTES.REGISTER, icon: 'UserPlus' },
]