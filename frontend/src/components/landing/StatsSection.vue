<script setup lang="ts">
import { Card, CardContent } from '@/components/ui/Card'
import { LANDING_CONTENT } from '@/constants'

const { stats } = LANDING_CONTENT
</script>

<template>
  <section class="border-y border-border bg-background/80 backdrop-blur-md px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-3 sm:gap-8">
        <Card v-for="stat in stats" :key="stat.label" class="border border-border/50 bg-background/90 backdrop-blur-md p-6 rounded-2xl shadow-sm hover:border-primary/30 transition-colors">
          <CardContent class="flex flex-col items-center p-0 text-center">
            <p class="text-4xl font-bold tracking-tight text-foreground lg:text-5xl">
              {{ stat.value }}
            </p>
            <p class="mt-2 text-sm font-medium text-muted-foreground sm:text-base">
              {{ stat.label }}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  </section>
</template>

