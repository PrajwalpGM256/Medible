<script setup lang="ts">
import AppNavbar from '@/components/common/AppNavbar.vue'
import AppFooter from '@/components/common/AppFooter.vue'
import HeroSection from '@/components/landing/HeroSection.vue'
import FeaturesSection from '@/components/landing/FeaturesSection.vue'
import StatsSection from '@/components/landing/StatsSection.vue'
import CTASection from '@/components/landing/CTASection.vue'
import AnimatedBackground from '@/components/animations/AnimatedBackground.vue'
import { RouterLink } from 'vue-router'
import { ROUTES } from '@/constants'
</script>

<template>
  <div class="relative flex min-h-screen flex-col">
    <AnimatedBackground />
    <AppNavbar />
    <main class="flex-1">
      <div class="w-full bg-teal-500/10 border-b border-teal-500/20 py-2 text-center z-10 relative backdrop-blur-sm">
        <RouterLink :to="ROUTES.LOGIN" class="text-sm font-medium text-teal-600 dark:text-teal-400 hover:underline">
          Use demo account to login
        </RouterLink>
      </div>
      <HeroSection />
      <FeaturesSection />
      <StatsSection />
      <CTASection />
    </main>
    <AppFooter />
  </div>
</template>

