<script setup lang="ts">
import { Pill, Apple, ShieldCheck, BookOpen } from 'lucide-vue-next'
import { Card, CardContent } from '@/components/ui/Card'
import { LANDING_CONTENT } from '@/constants'

const { features } = LANDING_CONTENT
const iconMap: Record<string, any> = { Pill, Apple, ShieldCheck, BookOpen }
</script>

<template>
  <section class="px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="mx-auto max-w-2xl text-center">
        <h2 class="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">Everything you need to stay safe</h2>
        <p class="mt-4 text-lg text-muted-foreground">Powerful features designed to help you understand your medications better.</p>
      </div>
      <div class="mt-12 grid gap-6 sm:mt-16 sm:grid-cols-2 lg:grid-cols-4">
        <Card v-for="feature in features" :key="feature.title" class="group relative overflow-hidden border-border transition-all hover:border-primary/50 hover:shadow-lg">
          <CardContent class="p-6">
            <div class="mb-4 inline-flex rounded-xl bg-gradient-to-br from-teal-500/10 to-cyan-500/10 p-3">
              <component :is="iconMap[feature.icon]" class="h-6 w-6 text-teal-600 dark:text-teal-400" />
            </div>
            <h3 class="mb-2 font-semibold text-foreground">{{ feature.title }}</h3>
            <p class="text-sm text-muted-foreground">{{ feature.description }}</p>
          </CardContent>
          <div class="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-teal-500 to-cyan-500 opacity-0 transition-opacity group-hover:opacity-100" />
        </Card>
      </div>
    </div>
  </section>
</template>
