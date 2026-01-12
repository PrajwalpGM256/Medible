<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { Eye, EyeOff, LogIn } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import AppLogo from '@/components/common/AppLogo.vue'
import { useAuthStore } from '@/stores/auth'
import { ROUTES, FORM_CONTENT } from '@/constants'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { login: content } = FORM_CONTENT

const email = ref('')
const password = ref('')
const showPassword = ref(false)

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
  <div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-background to-muted p-4">
    <div class="w-full max-w-md">
      <div class="mb-8 flex justify-center">
        <RouterLink :to="ROUTES.LANDING"><AppLogo size="lg" /></RouterLink>
      </div>
      <Card>
        <CardHeader class="text-center">
          <CardTitle class="text-2xl">{{ content.title }}</CardTitle>
          <CardDescription>{{ content.subtitle }}</CardDescription>
        </CardHeader>
        <CardContent>
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div class="space-y-2">
              <Label for="email">{{ content.emailLabel }}</Label>
              <Input id="email" v-model="email" type="email" placeholder="you@example.com" required />
            </div>
            <div class="space-y-2">
              <Label for="password">{{ content.passwordLabel }}</Label>
              <div class="relative">
                <Input id="password" v-model="password" :type="showPassword ? 'text' : 'password'" placeholder="••••••••" required />
                <Button type="button" variant="ghost" size="icon" class="absolute right-0 top-0 h-full px-3" @click="showPassword = !showPassword">
                  <EyeOff v-if="showPassword" class="h-4 w-4" /><Eye v-else class="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div v-if="auth.error" class="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">{{ auth.error }}</div>
            <Button type="submit" class="w-full gap-2" :disabled="auth.loading">
              <LogIn class="h-4 w-4" />{{ auth.loading ? 'Signing in...' : content.submitButton }}
            </Button>
          </form>
          <p class="mt-6 text-center text-sm text-muted-foreground">
            {{ content.noAccount }}
            <RouterLink :to="ROUTES.REGISTER" class="font-medium text-primary hover:underline">{{ content.signUp }}</RouterLink>
          </p>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
