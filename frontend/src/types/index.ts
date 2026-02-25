// User & Auth
export interface User {
  id: number
  email: string
  first_name?: string
  last_name?: string
  full_name?: string
  name?: string // Computed from full_name for convenience
  created_at?: string
  createdAt?: string // Alias for frontend compatibility
  is_active?: boolean
  is_admin?: boolean
  is_deleted?: boolean
  last_login_at?: string
  medication_count?: number
}

export interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
  error: string | null
}

export interface AdminStats {
  users: {
    total: number
    active: number
  }
  content: {
    total_medications: number
    total_food_logs: number
    total_interaction_checks: number
    total_searches: number
    total_interaction_reports: number
  }
  top_drugs: { drug_name: string; count: number }[]
  top_foods: { food_name: string; count: number }[]
}

// Medications
export interface Medication {
  id: number
  drugName: string
  genericName?: string
  dosage?: string
  frequency?: string
  instructions?: string
  createdAt: string
}

export interface DrugSearchResult {
  brandName: string
  genericName: string
  manufacturer?: string
  route?: string
  activeIngredients?: string[]
}

// Interactions
export type Severity = 'low' | 'moderate' | 'high'

export interface Interaction {
  id: number
  drugName: string
  foodName: string
  food?: string       // From getByDrug API payload
  foodCategory: string
  severity: Severity
  effect: string
  mechanism?: string
  recommendation: string
  evidenceLevel?: 'established' | 'probable' | 'suspected'
}

// Foods
export interface Food {
  fdcId: string
  description: string
  category?: string
  nutrients?: Nutrient[]
}

export interface Nutrient {
  name: string
  amount: number
  unit: string
}

// API Responses
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  perPage: number
}

// UI Types
export type Theme = 'light' | 'dark' | 'system'

export interface NavItem {
  label: string
  to: string
  icon?: string
  requiresAuth?: boolean
}

export interface SelectOption {
  label: string
  value: string
}