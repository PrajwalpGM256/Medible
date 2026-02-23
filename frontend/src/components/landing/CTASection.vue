<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { ArrowRight } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { ROUTES } from '@/constants'
</script>

<template>
  <section class="px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
    <div class="mx-auto max-w-4xl">
      <Card class="relative overflow-hidden border-none bg-gradient-to-br from-teal-500 to-cyan-600 shadow-2xl">
        <div class="absolute inset-0 opacity-10">
          <svg class="h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs>
              <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 10 0 L 0 0 0 10" fill="none" stroke="white" stroke-width="0.5"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)"/>
          </svg>
        </div>
        
        <CardContent class="relative flex flex-col items-center px-6 py-12 text-center sm:px-12 sm:py-16">
          <h2 class="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Ready to take control of your health?
          </h2>
          <p class="mx-auto mt-4 max-w-xl text-lg text-teal-100">
            Join thousands of users who trust Medible to keep them safe. Start for free today.
          </p>
          <div class="mt-10">
            <RouterLink :to="ROUTES.REGISTER">
              <Button size="lg" variant="secondary" hover="glow" class="h-12 px-8 text-base font-semibold shadow-lg">
                Get Started Now
                <ArrowRight class="ml-2 h-5 w-5" />
              </Button>
            </RouterLink>
          </div>
        </CardContent>
      </Card>
    </div>
  </section>
</template>

