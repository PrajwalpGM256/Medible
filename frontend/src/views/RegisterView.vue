<script setup lang="ts">
import AppNavbar from '@/components/common/AppNavbar.vue'
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { Eye, EyeOff, UserPlus } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import AppLogo from '@/components/common/AppLogo.vue'
import { useAuthStore } from '@/stores/auth'
import { ROUTES, FORM_CONTENT } from '@/constants'

const router = useRouter()
const auth = useAuthStore()
const { register: content } = FORM_CONTENT

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const localError = ref('')

async function handleSubmit() {
  localError.value = ''
  if (password.value !== confirmPassword.value) {
    localError.value = 'Passwords do not match'
    return
  }
  const success = await auth.register(name.value, email.value, password.value)
  if (success) router.push(ROUTES.DASHBOARD)
}
</script>

<template>
  <div>
    <AppNavbar />
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
              <Label for="name">{{ content.nameLabel }}</Label>
              <Input id="name" v-model="name" type="text" placeholder="John Doe" required />
            </div>
            <div class="space-y-2">
              <Label for="email">{{ content.emailLabel }}</Label>
              <Input id="email" v-model="email" type="email" placeholder="you@example.com" required />
            </div>
            <div class="space-y-2">
              <Label for="password">{{ content.passwordLabel }}</Label>
              <div class="relative">
                <Input id="password" v-model="password" :type="showPassword ? 'text' : 'password'" placeholder="••••••••" required minlength="8" />
                <Button type="button" variant="ghost" size="icon" class="absolute right-0 top-0 h-full px-3" @click="showPassword = !showPassword">
                  <EyeOff v-if="showPassword" class="h-4 w-4" /><Eye v-else class="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div class="space-y-2">
              <Label for="confirmPassword">{{ content.confirmPasswordLabel }}</Label>
              <Input id="confirmPassword" v-model="confirmPassword" type="password" placeholder="••••••••" required />
            </div>
            <div v-if="localError || auth.error" class="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">{{ localError || auth.error }}</div>
            <Button type="submit" class="w-full gap-2" :disabled="auth.loading">
              <UserPlus class="h-4 w-4" />{{ auth.loading ? 'Creating account...' : content.submitButton }}
            </Button>
          </form>
          <p class="mt-6 text-center text-sm text-muted-foreground">
            {{ content.hasAccount }}
            <RouterLink :to="ROUTES.LOGIN" class="font-medium text-primary hover:underline">{{ content.signIn }}</RouterLink>
          </p>
        </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
