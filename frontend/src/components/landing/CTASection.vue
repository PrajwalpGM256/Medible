<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { ArrowRight } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { ROUTES } from '@/constants'
</script>

<template>
  <section class="px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
    <div class="mx-auto max-w-4xl">
      <div class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-teal-500 to-cyan-600 px-6 py-12 text-center shadow-2xl sm:px-12 sm:py-16">
        <div class="absolute inset-0 opacity-10">
          <svg class="h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="white" stroke-width="0.5"/></pattern></defs>
            <rect width="100%" height="100%" fill="url(#grid)"/>
          </svg>
        </div>
        <div class="relative">
          <h2 class="text-2xl font-bold text-white sm:text-3xl lg:text-4xl">Ready to take control of your health?</h2>
          <p class="mx-auto mt-4 max-w-xl text-teal-100">Join thousands of users who trust Medible to keep them safe. Start for free today.</p>
          <div class="mt-8">
            <RouterLink :to="ROUTES.REGISTER">
              <Button size="lg" variant="secondary" class="gap-2">Get Started Now<ArrowRight class="h-4 w-4" /></Button>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
