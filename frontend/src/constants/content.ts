export const APP_NAME = 'Medible'
export const APP_TAGLINE = 'Know What You Eat With What You Take'
export const APP_DESCRIPTION = 'Your personal food-drug interaction checker. Stay safe by understanding how your medications interact with the foods you eat.'

export const LANDING_CONTENT = {
  hero: {
    title: 'Your Medications.',
    titleHighlight: 'Your Food.',
    titleEnd: 'Made Safe.',
    subtitle: APP_DESCRIPTION,
    cta: 'Get Started Free',
    secondaryCta: 'Learn More',
  },
  features: [
    {
      icon: 'Pill',
      title: 'Track Medications',
      description: 'Keep all your medications in one place with dosage and schedule tracking.',
    },
    {
      icon: 'Apple',
      title: 'Food Interaction Check',
      description: 'Instantly check if your meal is safe with your current medications.',
    },
    {
      icon: 'ShieldCheck',
      title: 'Safety Alerts',
      description: 'Get real-time alerts about potentially dangerous food-drug combinations.',
    },
    {
      icon: 'BookOpen',
      title: 'Learn & Understand',
      description: 'Detailed explanations of why certain foods affect your medications.',
    },
  ],
  stats: [
    { value: '500+', label: 'Drug Interactions' },
    { value: '1000+', label: 'Food Items' },
    { value: '24/7', label: 'Available' },
  ],
} as const

export const DASHBOARD_CONTENT = {
  welcome: 'Welcome back',
  quickActions: 'Quick Actions',
  recentInteractions: 'Recent Alerts',
  myMedications: 'My Medications',
  noMedications: 'No medications added yet',
  addFirst: 'Add your first medication to get started',
} as const

export const FORM_CONTENT = {
  login: {
    title: 'Welcome Back',
    subtitle: 'Sign in to your account',
    emailLabel: 'Email',
    passwordLabel: 'Password',
    submitButton: 'Sign In',
    forgotPassword: 'Forgot password?',
    noAccount: "Don't have an account?",
    signUp: 'Sign up',
  },
  register: {
    title: 'Create Account',
    subtitle: 'Start your journey to safer medication management',
    nameLabel: 'Full Name',
    emailLabel: 'Email',
    passwordLabel: 'Password',
    confirmPasswordLabel: 'Confirm Password',
    submitButton: 'Create Account',
    hasAccount: 'Already have an account?',
    signIn: 'Sign in',
  },
} as const

export const ERROR_MESSAGES = {
  generic: 'Something went wrong. Please try again.',
  network: 'Network error. Please check your connection.',
  unauthorized: 'Please sign in to continue.',
  notFound: 'The requested resource was not found.',
  validation: 'Please check your input and try again.',
} as const