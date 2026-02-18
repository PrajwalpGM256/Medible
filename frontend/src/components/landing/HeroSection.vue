<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { ArrowRight, Play, Pill, TriangleAlert } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import { ROUTES, LANDING_CONTENT } from '@/constants'

const { hero } = LANDING_CONTENT
</script>

<template>
  <section class="relative overflow-hidden px-4 pb-16 pt-12 sm:px-6 sm:pb-24 sm:pt-20 lg:px-8">
    <div class="mx-auto max-w-4xl text-center">
      <h1 class="text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl bg-background/30 backdrop-blur-[2px] rounded-2xl py-2">
        {{ hero.title }}
        <span class="bg-gradient-to-r from-teal-500 to-cyan-500 bg-clip-text text-transparent">{{ hero.titleHighlight }}</span>
        <br />{{ hero.titleEnd }}
      </h1>
      <p class="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl bg-background/50 backdrop-blur-[1px] rounded-xl p-2">{{ hero.subtitle }}</p>
      <div class="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
        <RouterLink :to="ROUTES.REGISTER">
          <Button size="lg" hover class="w-full gap-2 sm:w-auto">{{ hero.cta }}<ArrowRight class="h-4 w-4" /></Button>
        </RouterLink>
        <a href="#how-it-works" class="w-full sm:w-auto">
          <Button variant="outline" hover size="lg" class="w-full gap-2 sm:w-auto">
            <Play class="h-4 w-4" />
            {{ hero.secondaryCta }}
          </Button>
        </a>
      </div>
      <div class="relative mx-auto mt-16 max-w-3xl">
        <Card class="overflow-hidden rounded-2xl bg-background/90 backdrop-blur-xl shadow-2xl border-border/50">
          <div class="flex items-center gap-2 border-b border-border bg-muted/30 px-4 py-3">
            <div class="h-3 w-3 rounded-full bg-red-400" />
            <div class="h-3 w-3 rounded-full bg-yellow-400" />
            <div class="h-3 w-3 rounded-full bg-green-400" />
          </div>
          <CardContent class="p-6 sm:p-8">
            <div class="space-y-4">
              <div class="flex items-center gap-3 rounded-xl bg-background/80 p-4 shadow-sm border border-border/50 backdrop-blur-sm">
                <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500/10">
                  <Pill class="h-5 w-5 text-teal-600" />
                </div>
                <div class="flex-1 text-left">
                  <p class="font-medium text-foreground">Warfarin 5mg</p>
                  <p class="text-sm text-muted-foreground">Once daily</p>
                </div>
              </div>
              
              <Alert class="border-amber-400 bg-amber-50 text-left dark:border-amber-800 dark:bg-amber-950 border-2">
                <TriangleAlert class="h-4 w-4 text-amber-400 dark:text-amber-400" />
                <AlertTitle class="text-amber-700 dark:text-amber-300">Grapefruit Alert</AlertTitle>
                <AlertDescription class="text-amber-600 dark:text-amber-400">
                  May increase bleeding risk
                </AlertDescription>
              </Alert>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </section>
</template>

