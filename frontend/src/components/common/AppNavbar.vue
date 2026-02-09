<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { Menu, X } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import AppLogo from './AppLogo.vue'
import ThemeToggle from './ThemeToggle.vue'
import { useAuthStore } from '@/stores/auth'
import { ROUTES, NAV_ITEMS } from '@/constants'
import { ACTIVE_TAB_BG_COLOR } from '@/constants/theme'

const auth = useAuthStore()
const router = useRouter()
const mobileMenuOpen = ref(false)
const toggleMenu = () => { mobileMenuOpen.value = !mobileMenuOpen.value }
const route = router.currentRoute

function handleLogout() {
  auth.logout()
  router.push(ROUTES.LOGIN)
}
</script>

<template>
  <nav class="sticky top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-lg">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 items-center justify-between">
        <RouterLink :to="auth.isAuthenticated ? ROUTES.DASHBOARD : ROUTES.LANDING" class="flex-shrink-0">
          <AppLogo size="md" />
        </RouterLink>
        <div class="hidden items-center gap-1 md:flex">
          <template v-if="auth.isAuthenticated">
            <RouterLink
              v-for="item in NAV_ITEMS"
              :key="item.to"
              :to="item.to"
              :class="[
                'rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                route.path === item.to
                  ? `${ACTIVE_TAB_BG_COLOR} text-foreground font-semibold shadow`
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground'
              ]"
            >
              {{ item.label }}
            </RouterLink>
          </template>
        </div>
        <div class="flex items-center gap-2">
          <ThemeToggle />
          <template v-if="!auth.isAuthenticated">
            <RouterLink :to="ROUTES.LOGIN" class="hidden sm:block">
              <Button variant="ghost">Sign In</Button>
            </RouterLink>
            <RouterLink :to="ROUTES.REGISTER">
              <Button>Get Started</Button>
            </RouterLink>
          </template>
          <template v-else>
            <RouterLink :to="ROUTES.PROFILE" class="hidden sm:block">
              <Button variant="ghost">Profile</Button>
            </RouterLink>
            <Button variant="outline" @click="handleLogout">Logout</Button>
          </template>
          <Button variant="ghost" size="icon" class="md:hidden" @click="toggleMenu">
            <Menu v-if="!mobileMenuOpen" class="h-5 w-5" />
            <X v-else class="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
    <div v-if="mobileMenuOpen" class="border-t border-border bg-background md:hidden">
      <div class="space-y-1 px-4 py-3">
        <template v-if="auth.isAuthenticated">
          <RouterLink
            v-for="item in NAV_ITEMS"
            :key="item.to"
            :to="item.to"
            :class="[
              'block rounded-lg px-3 py-2 text-base font-medium',
              route.path === item.to
                ? `${ACTIVE_TAB_BG_COLOR} text-foreground font-semibold shadow`
                : 'text-foreground hover:bg-accent'
            ]"
            @click="mobileMenuOpen = false"
          >
            {{ item.label }}
          </RouterLink>
        </template>
        <template v-else>
          <RouterLink :to="ROUTES.LOGIN" class="block rounded-lg px-3 py-2 text-base font-medium text-foreground hover:bg-accent" @click="mobileMenuOpen = false">Sign In</RouterLink>
        </template>
      </div>
    </div>
  </nav>
</template>
