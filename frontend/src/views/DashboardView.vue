<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { Pill, AlertTriangle, Search, Plus, ArrowRight, BookOpen } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import AppNavbar from '@/components/common/AppNavbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { useAuthStore } from '@/stores/auth'
import { useMedicationsStore } from '@/stores/medications'
import { ROUTES, DASHBOARD_CONTENT, SEVERITY_CONFIG } from '@/constants'
import { interactionHistoryApi } from '@/services/api'

const auth = useAuthStore()
const meds = useMedicationsStore()

// Interaction history stats
const interactionHistory = ref<any[]>([])
const historyLoading = ref(false)

const historyHighRiskCount = computed(() => 
  interactionHistory.value.filter(h => h.max_severity === 'high').length
)
const historyTotalChecks = computed(() => interactionHistory.value.length)

async function fetchInteractionHistory() {
  historyLoading.value = true
  try {
    const { data } = await interactionHistoryApi.getAll(50)
    interactionHistory.value = data?.data?.history || []
  } catch (err) {
    console.error('Failed to fetch interaction history:', err)
  } finally {
    historyLoading.value = false
  }
}

onMounted(() => { 
  meds.fetchMedications()
  fetchInteractionHistory()
})

const quickActions = [
  { icon: Plus, label: 'Add Medication', to: ROUTES.MEDICATIONS, color: 'bg-teal-500' },
  { icon: BookOpen, label: 'Food Diary', to: ROUTES.FOOD_DIARY, color: 'bg-cyan-500' },
  { icon: Search, label: 'Check Interactions', to: ROUTES.INTERACTIONS, color: 'bg-amber-500' },
]
</script>

<template>
  <div class="min-h-screen bg-background">
    <AppNavbar />
    <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-foreground sm:text-3xl">{{ DASHBOARD_CONTENT.welcome }}, {{ auth.userName || 'there' }}! 👋</h1>
        <p class="mt-1 text-muted-foreground">Here's your medication overview</p>
      </div>
      <div class="mb-8 grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent class="flex items-center gap-4 p-6">
            <div class="rounded-xl bg-teal-500/10 p-3"><Pill class="h-6 w-6 text-teal-600 dark:text-teal-400" /></div>
            <div><p class="text-2xl font-bold text-foreground">{{ meds.count }}</p><p class="text-sm text-muted-foreground">Medications</p></div>
          </CardContent>
        </Card>
        <Card :class="{ 'border-amber-500/50': historyHighRiskCount > 0 }">
          <CardContent class="flex items-center gap-4 p-6">
            <div class="rounded-xl bg-amber-500/10 p-3"><AlertTriangle class="h-6 w-6 text-amber-600 dark:text-amber-400" /></div>
            <div><p class="text-2xl font-bold text-foreground">{{ historyHighRiskCount }}</p><p class="text-sm text-muted-foreground">High Risk Alerts</p></div>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="flex items-center gap-4 p-6">
            <div class="rounded-xl bg-emerald-500/10 p-3"><Search class="h-6 w-6 text-emerald-600 dark:text-emerald-400" /></div>
            <div><p class="text-2xl font-bold text-foreground">{{ historyTotalChecks }}</p><p class="text-sm text-muted-foreground">Interaction Checks</p></div>
          </CardContent>
        </Card>
      </div>
      <Card class="mb-8">
        <CardHeader><CardTitle>{{ DASHBOARD_CONTENT.quickActions }}</CardTitle></CardHeader>
        <CardContent>
          <div class="grid gap-3 sm:grid-cols-3">
            <RouterLink v-for="action in quickActions" :key="action.label" :to="action.to" class="flex items-center gap-3 rounded-xl border border-border p-4 transition-all hover:border-primary/50 hover:shadow-md">
              <div :class="[action.color, 'rounded-lg p-2']"><component :is="action.icon" class="h-5 w-5 text-white" /></div>
              <span class="font-medium text-foreground">{{ action.label }}</span>
              <ArrowRight class="ml-auto h-4 w-4 text-muted-foreground" />
            </RouterLink>
          </div>
        </CardContent>
      </Card>
      <div class="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader class="flex flex-row items-center justify-between">
            <CardTitle>{{ DASHBOARD_CONTENT.myMedications }}</CardTitle>
            <RouterLink :to="ROUTES.MEDICATIONS"><Button variant="ghost" size="sm">View All</Button></RouterLink>
          </CardHeader>
          <CardContent>
            <LoadingSpinner v-if="meds.loading" />
            <div v-else-if="meds.medications.length === 0" class="py-8 text-center">
              <Pill class="mx-auto h-12 w-12 text-muted-foreground/50" />
              <p class="mt-4 text-muted-foreground">{{ DASHBOARD_CONTENT.noMedications }}</p>
              <RouterLink :to="ROUTES.MEDICATIONS"><Button class="mt-4" size="sm"><Plus class="mr-2 h-4 w-4" />Add Medication</Button></RouterLink>
            </div>
            <div v-else class="space-y-3">
              <div v-for="med in meds.medications.slice(0, 4)" :key="med.id" class="flex items-center gap-3 rounded-lg border border-border p-3">
                <div class="rounded-lg bg-teal-500/10 p-2"><Pill class="h-4 w-4 text-teal-600 dark:text-teal-400" /></div>
                <div class="flex-1 truncate"><p class="font-medium text-foreground">{{ med.drugName }}</p><p class="text-sm text-muted-foreground">{{ med.dosage || 'No dosage set' }}</p></div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader class="flex flex-row items-center justify-between">
            <CardTitle>Recent Alerts</CardTitle>
            <RouterLink :to="ROUTES.INTERACTIONS"><Button variant="ghost" size="sm">View All</Button></RouterLink>
          </CardHeader>
          <CardContent>
            <LoadingSpinner v-if="historyLoading" />
            <div v-else-if="interactionHistory.length === 0" class="py-8 text-center">
              <AlertTriangle class="mx-auto h-12 w-12 text-muted-foreground/50" />
              <p class="mt-4 text-muted-foreground">No interaction checks yet</p>
            </div>
            <div v-else class="space-y-3">
              <div 
                v-for="check in interactionHistory.filter(h => h.had_interaction).slice(0, 4)" 
                :key="check.id" 
                :class="['rounded-lg border p-3', 
                  check.max_severity === 'high' ? 'bg-red-500/5 border-red-500/30' : 
                  check.max_severity === 'moderate' ? 'bg-amber-500/5 border-amber-500/30' : 
                  'bg-yellow-500/5 border-yellow-500/30']"
              >
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <p :class="['font-medium', 
                      check.max_severity === 'high' ? 'text-red-600 dark:text-red-400' : 
                      check.max_severity === 'moderate' ? 'text-amber-600 dark:text-amber-400' : 
                      'text-yellow-600 dark:text-yellow-400']">
                      {{ check.food_name }}
                    </p>
                    <p class="mt-1 text-sm text-muted-foreground">
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
              <div v-if="interactionHistory.filter(h => h.had_interaction).length === 0" class="py-4 text-center text-muted-foreground">
                No alerts - all checks are safe!
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  </div>
</template>
