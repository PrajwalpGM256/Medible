<script setup lang="ts">
import { computed } from 'vue'
import { Calendar } from 'lucide-vue-next'
import AppNavbar from '@/components/common/AppNavbar.vue'
import AnimatedBackground from '@/components/animations/AnimatedBackground.vue'
import EditProfileForm from '@/components/profile/EditProfileForm.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const memberSince = auth.user?.created_at
  ? new Date(auth.user.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  : 'Unknown'

const initials = computed(() => {
  const f = auth.user?.first_name?.[0] || ''
  const l = auth.user?.last_name?.[0] || ''
  return (f + l).toUpperCase() || '?'
})
</script>

<template>
  <div class="h-screen flex flex-col overflow-hidden bg-background">
    <AnimatedBackground />
    <AppNavbar />
    <main class="flex-1 min-h-0 flex flex-col items-center justify-center overflow-hidden px-4">
      <div class="w-full max-w-2xl space-y-6">
        <!-- Profile Header -->
        <div class="flex items-center gap-5">
          <div class="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-teal-500 to-emerald-600 text-2xl font-bold text-white shadow-xl ring-2 ring-teal-500/30 ring-offset-2 ring-offset-background">
            {{ initials }}
          </div>
          <div>
            <h1 class="text-2xl font-bold text-foreground">{{ auth.user?.full_name || 'User' }}</h1>
            <p class="text-sm text-muted-foreground">{{ auth.user?.email }}</p>
            <div class="flex items-center gap-1.5 mt-1">
              <Calendar class="h-3 w-3 text-muted-foreground/70" />
              <p class="text-xs text-muted-foreground/70">Member since {{ memberSince }}</p>
            </div>
          </div>
        </div>

        <!-- Profile Info Card (includes Profile Actions inside) -->
        <EditProfileForm />
      </div>
    </main>
  </div>
</template>
