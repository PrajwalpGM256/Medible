<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { ArrowRight, Play } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { ROUTES, LANDING_CONTENT } from '@/constants'

const { hero } = LANDING_CONTENT
</script>

<template>
  <section class="relative overflow-hidden px-4 pb-16 pt-12 sm:px-6 sm:pb-24 sm:pt-20 lg:px-8">
    <div class="absolute inset-0 -z-10">
      <div class="absolute left-1/2 top-0 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-to-br from-teal-400/20 to-cyan-400/20 blur-3xl" />
      <div class="absolute bottom-0 right-0 h-[400px] w-[400px] translate-x-1/4 translate-y-1/4 rounded-full bg-gradient-to-br from-cyan-400/20 to-teal-400/20 blur-3xl" />
    </div>
    <div class="mx-auto max-w-4xl text-center">
      <div class="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-background/50 px-4 py-1.5 text-sm backdrop-blur-sm">
        <span class="h-2 w-2 rounded-full bg-emerald-500" />
        <span class="text-muted-foreground">Trusted by 10,000+ users</span>
      </div>
      <h1 class="text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
        {{ hero.title }}
        <span class="bg-gradient-to-r from-teal-500 to-cyan-500 bg-clip-text text-transparent">{{ hero.titleHighlight }}</span>
        <br />{{ hero.titleEnd }}
      </h1>
      <p class="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl">{{ hero.subtitle }}</p>
      <div class="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
        <RouterLink :to="ROUTES.REGISTER">
          <Button size="lg" class="w-full gap-2 sm:w-auto">{{ hero.cta }}<ArrowRight class="h-4 w-4" /></Button>
        </RouterLink>
        <Button variant="outline" size="lg" class="w-full gap-2 sm:w-auto"><Play class="h-4 w-4" />{{ hero.secondaryCta }}</Button>
      </div>
      <div class="relative mx-auto mt-16 max-w-3xl">
        <div class="overflow-hidden rounded-2xl border border-border bg-gradient-to-b from-background to-muted/50 shadow-2xl">
          <div class="flex items-center gap-2 border-b border-border bg-muted/50 px-4 py-3">
            <div class="h-3 w-3 rounded-full bg-red-400" />
            <div class="h-3 w-3 rounded-full bg-yellow-400" />
            <div class="h-3 w-3 rounded-full bg-green-400" />
          </div>
          <div class="p-6 sm:p-8">
            <div class="space-y-4">
              <div class="flex items-center gap-3 rounded-xl bg-background p-4 shadow-sm">
                <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500/10"><span class="text-xl">💊</span></div>
                <div class="flex-1">
                  <p class="font-medium text-foreground">Warfarin 5mg</p>
                  <p class="text-sm text-muted-foreground">Once daily</p>
                </div>
              </div>
              <div class="flex items-center gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-950">
                <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-500/10"><span class="text-xl">⚠️</span></div>
                <div class="flex-1">
                  <p class="font-medium text-amber-700 dark:text-amber-300">Grapefruit Alert</p>
                  <p class="text-sm text-amber-600 dark:text-amber-400">May increase bleeding risk</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
