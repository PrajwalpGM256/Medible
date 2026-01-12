<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { AlertTriangle, CheckCircle, Info } from 'lucide-vue-next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import AppNavbar from '@/components/common/AppNavbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { useMedicationsStore } from '@/stores/medications'
import { SEVERITY_CONFIG } from '@/constants'
import type { Severity } from '@/types'

const meds = useMedicationsStore()

onMounted(() => { if (!meds.medications.length) meds.fetchMedications() })

const groupedInteractions = computed(() => {
  const groups: Record<Severity, typeof meds.interactions> = { high: [], moderate: [], low: [] }
  meds.interactions.forEach((i) => { groups[i.severity].push(i) })
  return groups
})

const severityIcons = { high: AlertTriangle, moderate: Info, low: CheckCircle }
</script>

<template>
  <div class="min-h-screen bg-background">
    <AppNavbar />
    <main class="mx-auto max-w-4xl px-4 py-6 sm:px-6 sm:py-8">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-foreground">Food Interactions</h1>
        <p class="text-muted-foreground">Foods to watch based on your medications</p>
      </div>
      <LoadingSpinner v-if="meds.loading" class="py-12" />
      <div v-else-if="!meds.interactions.length" class="py-12 text-center">
        <CheckCircle class="mx-auto h-12 w-12 text-emerald-500" />
        <p class="mt-4 text-lg font-medium text-foreground">No interactions found</p>
        <p class="mt-1 text-muted-foreground">Add medications to see potential food interactions</p>
      </div>
      <Tabs v-else default-value="all" class="w-full">
        <TabsList class="mb-6 w-full justify-start">
          <TabsTrigger value="all">All ({{ meds.interactions.length }})</TabsTrigger>
          <TabsTrigger value="high" class="text-red-600">High ({{ groupedInteractions.high.length }})</TabsTrigger>
          <TabsTrigger value="moderate" class="text-amber-600">Moderate ({{ groupedInteractions.moderate.length }})</TabsTrigger>
          <TabsTrigger value="low" class="text-emerald-600">Low ({{ groupedInteractions.low.length }})</TabsTrigger>
        </TabsList>
        <TabsContent value="all">
          <div class="space-y-4">
            <Card v-for="interaction in meds.interactions" :key="`${interaction.drugName}-${interaction.foodName}`" :class="SEVERITY_CONFIG[interaction.severity].borderClass">
              <CardHeader class="pb-2">
                <div class="flex items-start justify-between">
                  <div class="flex items-center gap-2">
                    <component :is="severityIcons[interaction.severity]" :class="['h-5 w-5', SEVERITY_CONFIG[interaction.severity].textClass]" />
                    <CardTitle class="text-lg">{{ interaction.drugName }} + {{ interaction.foodName }}</CardTitle>
                  </div>
                  <span :class="['rounded-full px-2.5 py-0.5 text-xs font-medium', SEVERITY_CONFIG[interaction.severity].bgClass, SEVERITY_CONFIG[interaction.severity].textClass]">{{ SEVERITY_CONFIG[interaction.severity].label }}</span>
                </div>
              </CardHeader>
              <CardContent>
                <p class="text-muted-foreground">{{ interaction.effect }}</p>
                <div class="mt-3 rounded-lg bg-muted/50 p-3">
                  <p class="text-sm font-medium text-foreground">Recommendation</p>
                  <p class="text-sm text-muted-foreground">{{ interaction.recommendation }}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        <TabsContent v-for="severity in (['high', 'moderate', 'low'] as Severity[])" :key="severity" :value="severity">
          <div class="space-y-4">
            <Card v-for="interaction in groupedInteractions[severity]" :key="`${interaction.drugName}-${interaction.foodName}`" :class="SEVERITY_CONFIG[severity].borderClass">
              <CardHeader class="pb-2"><CardTitle class="text-lg">{{ interaction.drugName }} + {{ interaction.foodName }}</CardTitle></CardHeader>
              <CardContent>
                <p class="text-muted-foreground">{{ interaction.effect }}</p>
                <div class="mt-3 rounded-lg bg-muted/50 p-3">
                  <p class="text-sm font-medium text-foreground">Recommendation</p>
                  <p class="text-sm text-muted-foreground">{{ interaction.recommendation }}</p>
                </div>
              </CardContent>
            </Card>
            <div v-if="!groupedInteractions[severity].length" class="py-8 text-center text-muted-foreground">No {{ severity }} risk interactions</div>
          </div>
        </TabsContent>
      </Tabs>
    </main>
  </div>
</template>
