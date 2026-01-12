<script setup lang="ts">
import { User, Mail, Calendar, LogOut } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import AppNavbar from '@/components/common/AppNavbar.vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ROUTES } from '@/constants'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push(ROUTES.LANDING)
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <AppNavbar />
    <main class="mx-auto max-w-2xl px-4 py-6 sm:px-6 sm:py-8">
      <h1 class="mb-6 text-2xl font-bold text-foreground">Profile</h1>
      <Card>
        <CardHeader><CardTitle>Account Information</CardTitle></CardHeader>
        <CardContent class="space-y-4">
          <div class="flex items-center gap-4 rounded-lg border border-border p-4">
            <div class="rounded-full bg-teal-500/10 p-3"><User class="h-6 w-6 text-teal-600 dark:text-teal-400" /></div>
            <div><p class="text-sm text-muted-foreground">Name</p><p class="font-medium text-foreground">{{ auth.user?.full_name || auth.user?.name || 'Not set' }}</p></div>
          </div>
          <div class="flex items-center gap-4 rounded-lg border border-border p-4">
            <div class="rounded-full bg-cyan-500/10 p-3"><Mail class="h-6 w-6 text-cyan-600 dark:text-cyan-400" /></div>
            <div><p class="text-sm text-muted-foreground">Email</p><p class="font-medium text-foreground">{{ auth.user?.email || 'Not set' }}</p></div>
          </div>
          <div class="flex items-center gap-4 rounded-lg border border-border p-4">
            <div class="rounded-full bg-emerald-500/10 p-3"><Calendar class="h-6 w-6 text-emerald-600 dark:text-emerald-400" /></div>
            <div><p class="text-sm text-muted-foreground">Member Since</p><p class="font-medium text-foreground">{{ auth.user?.created_at ? new Date(auth.user.created_at).toLocaleDateString() : 'Unknown' }}</p></div>
          </div>
        </CardContent>
      </Card>
      <Card class="mt-6">
        <CardHeader><CardTitle>Actions</CardTitle></CardHeader>
        <CardContent>
          <Button variant="destructive" class="w-full gap-2" @click="handleLogout"><LogOut class="h-4 w-4" />Sign Out</Button>
        </CardContent>
      </Card>
    </main>
  </div>
</template>
