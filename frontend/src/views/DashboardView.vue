<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { Pill, AlertTriangle, Search, Plus } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import AppNavbar from '@/components/common/AppNavbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { useAuthStore } from '@/stores/auth'
import { useMedicationsStore } from '@/stores/medications'
import { useInteractionHistoryStore } from '@/stores/interactionHistory'
import { ROUTES, DASHBOARD_CONTENT } from '@/constants'

const auth = useAuthStore()
const meds = useMedicationsStore()
const historyStore = useInteractionHistoryStore()

onMounted(() => { 
  // Smart fetch - only calls API if not already loaded
  meds.fetchMedications()
  historyStore.fetchHistory()
})

const userFirstName = computed(() => {
  if (auth.user?.first_name) return auth.user.first_name
  if (auth.userName) return auth.userName.split(' ')[0]
  return 'there'
})
</script>

<template>
  <div class="min-h-screen bg-background">
    <AppNavbar />
    <main class="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-4">
        <h1 class="text-xl font-bold text-foreground sm:text-2xl">{{ DASHBOARD_CONTENT.welcome }}, {{ userFirstName }}! 👋</h1>
        <p class="text-sm text-muted-foreground">Here's your medication overview</p>
      </div>

      <!-- Stats Row -->
      <div class="mb-4 grid gap-3 sm:grid-cols-3">
        <Card>
          <CardContent class="flex items-center gap-3 p-4">
            <div class="rounded-lg bg-teal-500/10 p-2"><Pill class="h-5 w-5 text-teal-600 dark:text-teal-400" /></div>
            <div><p class="text-xl font-bold text-foreground">{{ meds.count }}</p><p class="text-xs text-muted-foreground">Medications</p></div>
          </CardContent>
        </Card>
        <Card :class="{ 'border-amber-500/50': historyStore.highRiskCount > 0 }">
          <CardContent class="flex items-center gap-3 p-4">
            <div class="rounded-lg bg-amber-500/10 p-2"><AlertTriangle class="h-5 w-5 text-amber-600 dark:text-amber-400" /></div>
            <div><p class="text-xl font-bold text-foreground">{{ historyStore.highRiskCount }}</p><p class="text-xs text-muted-foreground">High Risk Alerts</p></div>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="flex items-center gap-3 p-4">
            <div class="rounded-lg bg-emerald-500/10 p-2"><Search class="h-5 w-5 text-emerald-600 dark:text-emerald-400" /></div>
            <div><p class="text-xl font-bold text-foreground">{{ historyStore.totalChecks }}</p><p class="text-xs text-muted-foreground">Interaction Checks</p></div>
          </CardContent>
        </Card>
      </div>

      <!-- Main Content Grid -->
      <div class="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader class="flex flex-row items-center justify-between py-3 px-4">
            <CardTitle class="text-base">{{ DASHBOARD_CONTENT.myMedications }}</CardTitle>
            <RouterLink :to="ROUTES.MEDICATIONS"><Button variant="ghost" size="sm" class="h-7 text-xs">View All</Button></RouterLink>
          </CardHeader>
          <CardContent class="px-4 pb-4 pt-0">
            <LoadingSpinner v-if="meds.loading" />
            <div v-else-if="meds.medications.length === 0" class="py-6 text-center">
              <Pill class="mx-auto h-10 w-10 text-muted-foreground/50" />
              <p class="mt-2 text-sm text-muted-foreground">{{ DASHBOARD_CONTENT.noMedications }}</p>
              <RouterLink :to="ROUTES.MEDICATIONS"><Button class="mt-3" size="sm"><Plus class="mr-2 h-4 w-4" />Add Medication</Button></RouterLink>
            </div>
            <div v-else class="space-y-2">
              <div v-for="med in meds.medications.slice(0, 4)" :key="med.id" class="flex items-center gap-2 rounded-md border border-border p-2">
                <div class="rounded-md bg-teal-500/10 p-1.5"><Pill class="h-3.5 w-3.5 text-teal-600 dark:text-teal-400" /></div>
                <div class="flex-1 truncate"><p class="text-sm font-medium text-foreground">{{ med.drugName }}</p><p class="text-xs text-muted-foreground">{{ med.dosage || 'No dosage set' }}</p></div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader class="flex flex-row items-center justify-between py-3 px-4">
            <CardTitle class="text-base">Recent Alerts</CardTitle>
            <RouterLink :to="ROUTES.INTERACTIONS"><Button variant="ghost" size="sm" class="h-7 text-xs">View All</Button></RouterLink>
          </CardHeader>
          <CardContent class="px-4 pb-4 pt-0">
            <LoadingSpinner v-if="historyStore.loading" />
            <div v-else-if="historyStore.history.length === 0" class="py-6 text-center">
              <AlertTriangle class="mx-auto h-10 w-10 text-muted-foreground/50" />
              <p class="mt-2 text-sm text-muted-foreground">No interaction checks yet</p>
            </div>
            <div v-else class="space-y-2">
              <div 
                v-for="check in historyStore.recentAlerts" 
                :key="check.id" 
                :class="['rounded-md border p-2', 
                  check.max_severity === 'high' ? 'bg-red-500/5 border-red-500/30' : 
                  check.max_severity === 'moderate' ? 'bg-amber-500/5 border-amber-500/30' : 
                  'bg-yellow-500/5 border-yellow-500/30']"
              >
                <div class="flex items-center justify-between gap-2">
                  <div class="min-w-0 flex-1">
                    <p :class="['text-sm font-medium truncate', 
                      check.max_severity === 'high' ? 'text-red-600 dark:text-red-400' : 
                      check.max_severity === 'moderate' ? 'text-amber-600 dark:text-amber-400' : 
                      'text-yellow-600 dark:text-yellow-400']">
                      {{ check.food_name }}
                    </p>
                    <p class="text-xs text-muted-foreground">
                      {{ check.interaction_count }} interaction(s) · {{ check.medications_checked?.length || 0 }} medication(s)
                    </p>
                  </div>
                  <span :class="['shrink-0 rounded-full px-2 py-0.5 text-xs font-medium',
                    check.max_severity === 'high' ? 'bg-red-500/10 text-red-600 dark:text-red-400' : 
                    check.max_severity === 'moderate' ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400' : 
                    'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400']">
                    {{ check.max_severity === 'high' ? 'High Risk' : check.max_severity === 'moderate' ? 'Moderate' : 'Low Risk' }}
                  </span>
                </div>
              </div>
              <div v-if="historyStore.recentAlerts.length === 0" class="py-3 text-center text-sm text-muted-foreground">
                No alerts - all checks are safe!
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  </div>
</template>
