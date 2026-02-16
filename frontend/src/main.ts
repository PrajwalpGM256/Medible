import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/index.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Token validation happens in App.vue onMounted
// This ensures proper async handling and redirect on invalid token

app.mount('#app')