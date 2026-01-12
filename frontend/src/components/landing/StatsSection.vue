<script setup lang="ts">
import { LANDING_CONTENT } from '@/constants'

const { stats } = LANDING_CONTENT
</script>

<template>
  <section class="border-y border-border bg-muted/30 px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="grid grid-cols-3 gap-8 text-center">
        <div v-for="stat in stats" :key="stat.label">
          <p class="text-3xl font-bold text-foreground sm:text-4xl lg:text-5xl">{{ stat.value }}</p>
          <p class="mt-2 text-sm text-muted-foreground sm:text-base">{{ stat.label }}</p>
        </div>
      </div>
    </div>
  </section>
</template>
