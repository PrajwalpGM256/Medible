<script setup lang="ts">
import AppNavbar from '@/components/common/AppNavbar.vue'
import AppFooter from '@/components/common/AppFooter.vue'
import HeroSection from '@/components/landing/HeroSection.vue'
import FeaturesSection from '@/components/landing/FeaturesSection.vue'
import StatsSection from '@/components/landing/StatsSection.vue'
import CTASection from '@/components/landing/CTASection.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <AppNavbar />
    <main class="flex-1">
      <HeroSection />
      <FeaturesSection />
      <StatsSection />
      <CTASection />
    </main>
    <AppFooter />
  </div>
</template>
