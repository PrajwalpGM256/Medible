<script setup lang="ts">
import { Pill, Apple, ShieldCheck, BookOpen, Search, Utensils, ShieldAlert, ArrowRight } from 'lucide-vue-next'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import SectionHeader from '@/components/common/SectionHeader.vue'
import { LANDING_CONTENT } from '@/constants'

const { features } = LANDING_CONTENT
const iconMap: Record<string, any> = { Pill, Apple, ShieldCheck, BookOpen }

const steps = [
  {
    icon: Search,
    title: 'Search Meds',
    description: 'Find your prescriptions in our extensive database powered by OpenFDA.'
  },
  {
    icon: Utensils,
    title: 'Log Food',
    description: 'Search for foods or ingredients to see their nutritional profile.'
  },
  {
    icon: ShieldAlert,
    title: 'Check Safety',
    description: 'Get instant alerts if your food choice interacts with your medications.'
  }
]
</script>

<template>
  <section class="relative px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
    <!-- Decorative background element -->
    <div class="absolute left-1/2 top-1/2 -z-10 h-[400px] w-[800px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-teal-500/5 blur-[120px]" />

    <div class="mx-auto max-w-7xl">
      <SectionHeader 
        title="Everything you need to stay safe"
        subtitle="Powerful features designed to help you understand your medications better."
      />
      
      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card 
          v-for="feature in features" 
          :key="feature.title" 
          class="group relative overflow-hidden transition-all hover:border-primary/50 hover:shadow-lg"
        >
          <CardHeader class="pb-2">
            <div class="mb-2 inline-flex w-fit rounded-xl bg-gradient-to-br from-teal-500/10 to-cyan-500/10 p-3">
              <component :is="iconMap[feature.icon]" class="h-6 w-6 text-teal-600 dark:text-teal-400" />
            </div>
            <CardTitle class="text-xl">{{ feature.title }}</CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription class="text-sm text-muted-foreground">
              {{ feature.description }}
            </CardDescription>
          </CardContent>
          <div class="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-teal-500 to-cyan-500 opacity-0 transition-opacity group-hover:opacity-100" />
        </Card>
      </div>

      <!-- How It Works Section -->
      <div id="how-it-works" class="mt-24 sm:mt-32 scroll-mt-24">
        <SectionHeader 
          title="How it works"
          subtitle="Three simple steps to safety."
          class="mb-12"
        />

        <div class="relative mx-auto flex flex-col items-center gap-8 lg:flex-row lg:items-start lg:justify-center lg:gap-4">
          <template v-for="(step, index) in steps" :key="step.title">
            <div class="flex flex-col items-center text-center max-w-sm">
              <div class="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-background/95 backdrop-blur-sm border-2 border-teal-500/20 shadow-xl group hover:border-teal-500/50 transition-colors">
                <component :is="step.icon" class="h-8 w-8 text-teal-600 dark:text-teal-400 group-hover:scale-110 transition-transform" />
              </div>
              <h3 class="mb-3 text-xl font-bold text-foreground">{{ step.title }}</h3>
              <p class="text-muted-foreground leading-relaxed bg-background/50 rounded-lg p-2 backdrop-blur-[2px]">{{ step.description }}</p>
            </div>
            
            <!-- Arrow -->
            <div v-if="index < steps.length - 1" class="flex items-center justify-center py-4 lg:py-0 lg:px-4 lg:h-16">
              <ArrowRight class="h-6 w-6 text-teal-500/40 rotate-90 lg:rotate-0" />
            </div>
          </template>
        </div>
      </div>
    </div>
  </section>
</template>


