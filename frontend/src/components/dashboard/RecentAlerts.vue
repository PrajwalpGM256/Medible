<script setup lang="ts">
import { AlertTriangle, ChevronRight, Info } from 'lucide-vue-next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/skeleton'
import { ROUTES } from '@/constants'
import { RouterLink } from 'vue-router'

const props = defineProps<{
  alerts: any[]
  loading?: boolean
}>()

const getSeverityStyles = (severity: string) => {
  switch (severity) {
    case 'high':
      return {
        card: 'bg-red-500/5 border-red-500/20 hover:bg-red-500/10',
        text: 'text-red-600 dark:text-red-400',
        badge: 'bg-red-500/15 text-red-700 dark:text-red-300 border border-red-500/20',
        icon: 'text-red-500'
      }
    case 'moderate':
      return {
        card: 'bg-amber-500/5 border-amber-500/20 hover:bg-amber-500/10',
        text: 'text-amber-600 dark:text-amber-400',
        badge: 'bg-amber-500/15 text-amber-700 dark:text-amber-300 border border-amber-500/20',
        icon: 'text-amber-500'
      }
    default:
      return {
        card: 'bg-yellow-500/5 border-yellow-500/20 hover:bg-yellow-500/10',
        text: 'text-yellow-600 dark:text-yellow-400',
        badge: 'bg-yellow-500/15 text-yellow-700 dark:text-yellow-300 border border-yellow-500/20',
        icon: 'text-yellow-500'
      }
  }
}
</script>

<template>
  <Card variant="glass" hover="glow" class="h-full">
    <CardHeader class="flex flex-row items-center justify-between py-2 px-3">
      <CardTitle class="text-lg font-semibold flex items-center gap-2">
        <AlertTriangle class="h-5 w-5 text-amber-500" />
        Recent Alerts
      </CardTitle>
      <RouterLink :to="ROUTES.INTERACTIONS">
        <Button variant="ghost" size="sm" class="h-8 px-3 text-xs font-medium hover:bg-accent/50">
          View History
          <ChevronRight class="ml-1 h-3.5 w-3.5" />
        </Button>
      </RouterLink>
    </CardHeader>
    <CardContent class="px-3 pb-3 pt-0">
      <div v-if="loading" class="space-y-3">
        <Skeleton v-for="i in 3" :key="i" class="h-16 w-full rounded-xl" />
      </div>
      <div v-else-if="alerts.length === 0" class="py-10 text-center flex flex-col items-center gap-3">
        <div class="rounded-full bg-muted/50 p-4 border-2 border-dashed border-border/50">
          <Info class="h-10 w-10 text-muted-foreground/30" />
        </div>
        <div>
          <p class="text-base font-medium text-foreground">All systems clear!</p>
          <p class="text-sm text-muted-foreground mt-1">No potential interactions detected yet.</p>
        </div>
      </div>
      <div v-else class="space-y-3">
        <div 
          v-for="check in alerts" 
          :key="check.id" 
          :class="['group flex items-center justify-between rounded-xl border p-2 transition-all duration-300', getSeverityStyles(check.max_severity).card]"
        >
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <p :class="['text-base font-bold truncate leading-tight', getSeverityStyles(check.max_severity).text]">
                {{ check.food_name }}
              </p>
            </div>
            <p class="text-xs text-muted-foreground mt-1.5 flex items-center gap-1.5">
              <span class="inline-block w-1.5 h-1.5 rounded-full bg-muted-foreground/30"></span>
              {{ check.interaction_count }} interaction(s) detected
              <span class="inline-block w-1.5 h-1.5 rounded-full bg-muted-foreground/30 ml-1"></span>
              {{ check.medications_checked?.length || 0 }} medication(s) checked
            </p>
          </div>
          <div class="flex flex-col items-end gap-2 ml-4">
            <span :class="['shrink-0 rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider', getSeverityStyles(check.max_severity).badge]">
              {{ check.max_severity === 'high' ? 'High Risk' : check.max_severity === 'moderate' ? 'Moderate' : 'Low Risk' }}
            </span>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

