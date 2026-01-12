import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/index.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize auth state before mounting
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()

// If token exists, fetch user profile on app load
if (authStore.token) {
  authStore.fetchProfile()
}

app.mount('#app')