<script setup lang="ts">
import AppNavbar from '@/components/common/AppNavbar.vue'
import { ref } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { Eye, EyeOff, LogIn } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { useAuthStore } from '@/stores/auth'
import { ROUTES, FORM_CONTENT } from '@/constants'
import AnimatedBackground from '@/components/animations/AnimatedBackground.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { login: content } = FORM_CONTENT

const email = ref('')
const password = ref('')
const showPassword = ref(false)

function fillDemoCredentials() {
  email.value = 'demo@medible.com'
  password.value = 'Demo123!'
}

async function handleSubmit() {
  const success = await auth.login(email.value, password.value)
  if (success) {
    // Redirect to the original page or dashboard
    const redirectPath = (route.query.redirect as string) || ROUTES.DASHBOARD
    router.push(redirectPath)
  }
}
</script>

<template>
  <div class="relative flex h-screen flex-col overflow-hidden">
    <AnimatedBackground />
    <AppNavbar />
    <div class="flex flex-1 items-center justify-center p-4">
      <div class="w-full max-w-md">
        <Card class="border-2 border-teal-500/50 bg-background/80 backdrop-blur-md shadow-[0_0_20px_rgba(20,184,166,0.3)] dark:shadow-[0_0_30px_rgba(20,184,166,0.2)]">
        <CardHeader class="p-6 text-center">
          <CardTitle class="text-2xl">{{ content.title }}</CardTitle>
          <CardDescription>{{ content.subtitle }}</CardDescription>
        </CardHeader>
        <CardContent class="px-6 pb-6 pt-0">
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div class="space-y-2">
              <Label for="email">{{ content.emailLabel }}</Label>
              <Input id="email" v-model="email" type="email" variant="outline" placeholder="you@example.com" required class="autofill:bg-transparent autofill:text-inherit border-2 border-black dark:border-white focus-visible:ring-0 focus-visible:border-b-4 transition-all" />
            </div>
            <div class="space-y-2">
              <Label for="password">{{ content.passwordLabel }}</Label>
              <div class="relative">
                <Input id="password" v-model="password" :type="showPassword ? 'text' : 'password'" variant="outline" placeholder="••••••••" required class="autofill:bg-transparent autofill:text-inherit border-2 border-black dark:border-white focus-visible:ring-0 focus-visible:border-b-4 transition-all" />
                <Button type="button" variant="ghost" size="icon" class="absolute right-0 top-0 h-full px-3" @click="showPassword = !showPassword">
                  <EyeOff v-if="showPassword" class="h-4 w-4" /><Eye v-else class="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div v-if="auth.error" class="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">{{ auth.error }}</div>
            <div class="flex flex-col items-center gap-2">
              <Button 
                type="submit" 
                hover="active"
                class="w-fit gap-2 border-2 border-black dark:border-teal-500 font-semibold text-black transition-all duration-300 dark:text-teal-400 active:scale-[0.98]" 
                :disabled="auth.loading"
              >
                <LogIn class="h-4 w-4" />{{ auth.loading ? 'Signing in...' : content.submitButton }}
              </Button>
              <Button 
                type="button" 
                variant="outline" 
                size="sm"
                hover="glow"
                class="h-auto border-2 border-black dark:border-white text-m font-medium pb-1 pt-1" 
                @click="fillDemoCredentials"
              >
                Use Demo Account
              </Button>
            </div>
          </form>
          <p class="mt-6 text-center text-sm text-muted-foreground">
            {{ content.noAccount }}
            <RouterLink :to="ROUTES.REGISTER" class="font-medium text-primary hover:underline">{{ content.signUp }}</RouterLink>
          </p>
          <p class="mt-4 text-center text-xs text-amber-500 dark:text-amber-400 mx-auto max-w-sm font-medium">
            Note: First time login will cause a delay of ~1 minute to wait for the backend to start as it's on a free tier.
          </p>
        </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
