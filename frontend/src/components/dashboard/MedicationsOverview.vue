<script setup lang="ts">
import { Pill, Plus, ExternalLink, Activity } from 'lucide-vue-next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/skeleton'
import { ROUTES } from '@/constants'
import { RouterLink } from 'vue-router'

defineProps<{
  medications: any[]
  loading?: boolean
}>()
</script>

<template>
  <Card variant="glass" hover="glow" class="h-full">
    <CardHeader class="flex flex-row items-center justify-between py-2 px-3">
      <CardTitle class="text-lg font-semibold flex items-center gap-2">
        <Pill class="h-5 w-5 text-teal-500" />
        Current Medications
      </CardTitle>
      <RouterLink :to="ROUTES.MEDICATIONS">
        <Button variant="ghost" size="sm" class="h-8 px-3 text-xs font-medium hover:bg-accent/50">
          View All
          <ExternalLink class="ml-1 h-3.5 w-3.5" />
        </Button>
      </RouterLink>
    </CardHeader>
    <CardContent class="px-3 pb-3 pt-0">
      <div v-if="loading" class="space-y-3">
        <Skeleton v-for="i in 4" :key="i" class="h-14 w-full rounded-xl" />
      </div>
      <div v-else-if="medications.length === 0" class="py-10 text-center flex flex-col items-center gap-3">
        <div class="rounded-full bg-muted/50 p-4 border-2 border-dashed border-border/50">
          <Pill class="h-10 w-10 text-muted-foreground/30" />
        </div>
        <div>
          <p class="text-base font-medium text-foreground">No medications added</p>
          <p class="text-sm text-muted-foreground mt-1">Start by adding your current medications.</p>
        </div>
        <RouterLink :to="ROUTES.MEDICATIONS" class="mt-2">
          <Button size="sm" class="h-9 px-5 font-semibold bg-teal-600 hover:bg-teal-700 text-white shadow-md hover:shadow-teal-600/20">
            <Plus class="mr-2 h-4 w-4" />
            Add Medication
          </Button>
        </RouterLink>
      </div>
      <div v-else class="grid gap-2 sm:grid-cols-1">
        <div 
          v-for="med in medications.slice(0, 5)" 
          :key="med.id" 
          class="group flex items-center gap-3 rounded-xl border border-border bg-background/40 p-2 transition-all duration-300 hover:bg-accent/5 hover:border-teal-500/30 hover:shadow-sm"
        >
          <div class="rounded-lg bg-teal-500/10 p-2 transition-colors duration-300 group-hover:bg-teal-500/20">
            <Activity class="h-4 w-4 text-teal-600 dark:text-teal-400" />
          </div>
          <div class="flex-1 truncate">
            <p class="text-[15px] font-bold text-foreground leading-tight truncate group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors">
              {{ med.drugName }}
            </p>
            <p class="text-xs text-muted-foreground mt-0.5 font-medium truncate">
              {{ med.dosage || 'Dosage not set' }}
            </p>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

