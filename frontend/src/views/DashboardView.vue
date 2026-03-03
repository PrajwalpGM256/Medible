<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { Pill, AlertTriangle, Apple, Plus, ArrowUpRight, Flame, ShieldAlert, BadgeInfo } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import AppNavbar from '@/components/common/AppNavbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import { ROUTES, DASHBOARD_CONTENT } from '@/constants'
import AnimatedBackground from '@/components/animations/AnimatedBackground.vue'

const auth = useAuthStore()
const dashboard = useDashboardStore()

onMounted(() => { 
  dashboard.fetchDashboardData()
})

const userFirstName = computed(() => {
  if (dashboard.summary?.user?.first_name) return dashboard.summary.user.first_name
  if (auth.user?.first_name) return auth.user.first_name
  if (auth.userName) return auth.userName.split(' ')[0]
  return 'there'
})

const hasHighRiskAlerts = computed(() => {
  return dashboard.alerts.some(alert => alert.severity === 'high')
})
</script>

<template>
  <div class="h-screen overflow-hidden bg-background flex flex-col">
    <AnimatedBackground />
    <AppNavbar />
    <main class="mx-auto w-full max-w-7xl flex-1 flex flex-col px-4 py-4 sm:px-6 lg:px-8 min-h-0 overflow-y-auto lg:overflow-hidden">
      <!-- Header -->
      <div class="mb-4 flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-foreground sm:text-2xl">{{ DASHBOARD_CONTENT.welcome }}, {{ userFirstName }}! </h1>
          <p class="text-sm text-muted-foreground">Here is your daily health overview</p>
        </div>
        
        <!-- Streak Badge -->
        <div v-if="!dashboard.loading && dashboard.summary?.food_diary_streak" class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-500/10 border border-orange-500/20 shadow-sm animate-fade-in">
          <Flame class="h-5 w-5 text-orange-500" />
          <div class="text-sm font-medium">
            <span class="text-orange-600 dark:text-orange-400">{{ dashboard.summary.food_diary_streak }} Day</span>
            <span class="text-muted-foreground ml-1 hidden sm:inline">Logging Streak! </span>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="flex flex-col lg:grid gap-4 lg:grid-cols-2 lg:grid-rows-[auto_minmax(0,1fr)] flex-1 min-h-0 lg:min-h-0 min-h-max pb-4">
        <!-- Medications & Recents -->
        <div class="flex flex-col gap-4 min-h-0 order-2 lg:order-none lg:col-start-1 lg:row-start-1 lg:row-span-2">
          <!-- Medication Summary -->
          <Card variant="gold" class="bg-white/10 dark:bg-black/10 backdrop-blur-sm flex flex-col flex-1 min-h-0">
             <CardHeader class="flex flex-row items-center justify-between py-1.5 px-3">
              <div class="flex items-center gap-2">
                <div class="rounded-md bg-teal-500/10 p-1.5"><Pill class="h-4 w-4 text-teal-600 dark:text-teal-400" /></div>
                <CardTitle class="text-base">{{ DASHBOARD_CONTENT.myMedications }}</CardTitle>
              </div>
              <RouterLink :to="ROUTES.MEDICATIONS"><Button variant="ghost" size="icon" class="h-7 w-7 group"><ArrowUpRight class="h-4 w-4 transition-transform duration-200 group-hover:rotate-45" /></Button></RouterLink>
            </CardHeader>
            <CardContent class="px-4 pb-4 pt-0 flex-1 flex flex-col min-h-0">
              <div v-if="dashboard.loading" class="py-4 text-center text-sm text-muted-foreground">Loading...</div>
              <div v-else-if="!dashboard.summary?.medications.total" class="py-4 text-center">
                <p class="text-sm text-muted-foreground">No medications tracking yet.</p>
                <RouterLink :to="ROUTES.MEDICATIONS"><Button class="mt-3" size="sm" variant="outline"><Plus class="mr-2 h-4 w-4" />Add First Medication</Button></RouterLink>
              </div>
              <div v-else class="space-y-2 flex-1 min-h-0 overflow-y-auto scrollbar-hide pr-1">
                <RouterLink 
                  v-for="med in dashboard.summary.medications.list" 
                  :key="med.id"
                  :to="ROUTES.MEDICATIONS" 
                  class="flex items-center justify-between p-2 rounded-md border border-border bg-background/30 hover:bg-white/5 dark:hover:bg-white/10 transition-colors cursor-pointer group"
                >
                  <div class="flex items-center gap-3 truncate">
                     <div class="h-2 w-2 rounded-full shrink-0 bg-teal-500"></div>
                     <div class="flex flex-col truncate">
                       <span class="text-sm font-medium truncate capitalize transition-colors">{{ med.drug_name }}</span>
                       <span v-if="med.dosage" class="text-[10px] text-muted-foreground truncate">{{ med.dosage }} {{ med.frequency ? `• ${med.frequency}` : '' }}</span>
                     </div>
                  </div>
                </RouterLink>
              </div>
            </CardContent>
          </Card>

           <Card variant="gold" class="bg-white/10 dark:bg-black/10 backdrop-blur-sm flex flex-col flex-1 min-h-0">
            <CardHeader class="flex flex-row items-center justify-between py-1.5 px-3">
               <CardTitle class="text-base">Recent Check History</CardTitle>
               <RouterLink :to="ROUTES.INTERACTIONS"><Button variant="ghost" size="icon" class="h-7 w-7 group"><ArrowUpRight class="h-4 w-4 transition-transform duration-200 group-hover:rotate-45" /></Button></RouterLink>
            </CardHeader>
            <CardContent class="px-4 pb-4 pt-0 flex-1 flex flex-col min-h-0">
              <LoadingSpinner v-if="dashboard.loading" />
              <div v-else-if="!dashboard.summary?.recent_checks.length" class="py-6 text-center">
                <Apple class="mx-auto h-10 w-10 text-muted-foreground/50" />
                <p class="mt-2 text-sm text-muted-foreground">No interaction checks recently</p>
              </div>
              <div v-else class="space-y-2 flex-1 min-h-0 overflow-y-auto scrollbar-hide pr-1">
                <RouterLink v-for="check in dashboard.summary.recent_checks" :key="check.id" :to="ROUTES.INTERACTIONS" class="flex items-center justify-between p-2 rounded-md border border-border bg-background/30 hover:bg-white/5 dark:hover:bg-white/10 transition-colors cursor-pointer group">
                  <div class="flex items-center gap-3 truncate">
                     <div :class="['h-2 w-2 rounded-full shrink-0', check.had_interaction ? (check.max_severity === 'high' ? 'bg-red-500' : 'bg-amber-500') : 'bg-emerald-500']"></div>
                     <span class="text-sm font-medium truncate capitalize transition-colors">{{ check.food_name }}</span>
                  </div>
                   <span class="text-xs text-muted-foreground whitespace-nowrap">{{ new Date(check.checked_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) }}</span>
                </RouterLink>
              </div>
            </CardContent>
           </Card>
        </div>

        <!-- Daily Macros (Thin Row) -->
        <div class="grid grid-cols-4 gap-2 shrink-0 order-1 lg:order-none lg:col-start-2 lg:row-start-1">
            <!-- Calories -->
            <Card variant="gold" class="bg-white/10 dark:bg-black/10 backdrop-blur-sm flex flex-col items-center justify-center py-2 px-1 relative overflow-hidden group">
              <div class="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <span class="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">Calories</span>
              <span class="text-base font-bold leading-tight">{{ dashboard.loading ? '-' : dashboard.summary?.nutrition_today.calories || 0 }}</span>
            </Card>
            <!-- Protein -->
            <Card variant="gold" class="bg-white/10 dark:bg-black/10 backdrop-blur-sm flex flex-col items-center justify-center py-2 px-1 relative overflow-hidden group border-b-2 border-b-rose-500/50">
              <div class="absolute inset-0 bg-gradient-to-br from-rose-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <span class="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">Protein</span>
              <span class="text-base font-bold leading-tight">{{ dashboard.loading ? '-' : dashboard.summary?.nutrition_today.protein || 0 }}<span class="text-[9px] font-normal text-muted-foreground ml-0.5">g</span></span>
            </Card>
            <!-- Carbs -->
            <Card variant="gold" class="bg-white/10 dark:bg-black/10 backdrop-blur-sm flex flex-col items-center justify-center py-2 px-1 relative overflow-hidden group border-b-2 border-b-amber-500/50">
              <div class="absolute inset-0 bg-gradient-to-br from-amber-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <span class="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">Carbs</span>
              <span class="text-base font-bold leading-tight">{{ dashboard.loading ? '-' : dashboard.summary?.nutrition_today.carbs || 0 }}<span class="text-[9px] font-normal text-muted-foreground ml-0.5">g</span></span>
            </Card>
            <!-- Fat -->
            <Card variant="gold" class="bg-white/10 dark:bg-black/10 backdrop-blur-sm flex flex-col items-center justify-center py-2 px-1 relative overflow-hidden group border-b-2 border-b-cyan-500/50">
              <div class="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <span class="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">Fat</span>
              <span class="text-base font-bold leading-tight">{{ dashboard.loading ? '-' : dashboard.summary?.nutrition_today.fat || 0 }}<span class="text-[9px] font-normal text-muted-foreground ml-0.5">g</span></span>
            </Card>
          </div>

          <!-- Active Alerts Panel -->
          <Card variant="gold" :class="['bg-white/10 dark:bg-black/10 backdrop-blur-sm flex flex-col flex-1 min-h-[350px] lg:min-h-0 order-3 lg:order-none lg:col-start-2 lg:row-start-2', { 'ring-2 ring-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.2)]': hasHighRiskAlerts }]">
             <CardHeader class="flex flex-row items-center justify-between py-1.5 px-3 border-b border-border/50 bg-background/30">
            <div class="flex items-center gap-2">
               <ShieldAlert :class="['h-5 w-5', hasHighRiskAlerts ? 'text-red-500 animate-pulse' : 'text-emerald-500']" />
               <CardTitle class="text-base">Active Safety Alerts</CardTitle>
            </div>
            <BadgeInfo v-if="!dashboard.loading" class="h-5 w-5 text-muted-foreground" />
          </CardHeader>
          
          <CardContent class="p-0 flex-1 flex flex-col min-h-0 relative">
            <LoadingSpinner v-if="dashboard.alertsLoading" class="my-auto py-10" />
            
            <div v-else-if="dashboard.alerts.length === 0" class="flex-1 flex flex-col items-center justify-center p-8 text-center animate-in fade-in zoom-in duration-500">
              <div class="h-16 w-16 rounded-full bg-emerald-500/10 flex items-center justify-center mb-4">
                <ShieldAlert class="h-8 w-8 text-emerald-500" />
              </div>
              <h3 class="text-lg font-semibold text-emerald-600 dark:text-emerald-400 border-none m-0 p-0">All Clear!</h3>
              <p class="text-sm text-muted-foreground mt-2 max-w-[250px]">
                No FDA recalls for your medications, and no severe interactions detected in your meals today.
              </p>
            </div>

            <div v-else class="flex-1 min-h-0 overflow-y-auto p-4 space-y-3 scrollbar-hide">
              <div 
                v-for="(alert, idx) in dashboard.alerts" 
                :key="idx"
                class="rounded-lg border p-3 flex flex-col gap-2 relative overflow-hidden"
                 :class="[
                  alert.severity === 'high' ? 'bg-red-500/10 border-red-500/30' : 
                  'bg-amber-500/10 border-amber-500/30'
                ]"
              >
                <!-- Alert Header -->
                <div class="flex items-start justify-between gap-4">
                  <div class="flex items-center gap-2">
                    <AlertTriangle :class="['h-4 w-4 shrink-0', alert.severity === 'high' ? 'text-red-500' : 'text-amber-500']" />
                    <span class="font-semibold text-sm" :class="alert.severity === 'high' ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400'">
                      {{ alert.type === 'recall' ? 'FDA Drug Recall' : 'Severe Diet Interaction' }}
                    </span>
                  </div>
                  <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full" :class="alert.severity === 'high' ? 'bg-red-500/20 text-red-700 dark:text-red-300' : 'bg-amber-500/20 text-amber-700 dark:text-amber-300'">
                     {{ alert.type }}
                  </span>
                </div>

                <!-- Alert Body -->
                <div>
                   <h4 class="text-sm font-medium text-foreground leading-tight">{{ alert.title }}</h4>
                   <p class="text-xs text-muted-foreground mt-1">{{ alert.message }}</p>
                </div>

                <!-- Alert Footer Tags -->
                <div class="flex flex-wrap items-center gap-2 mt-1">
                   <div class="text-[10px] font-medium bg-background px-2 py-1 rounded-md border border-border">
                     💊 {{ alert.medication }}
                   </div>
                   <div v-if="alert.food" class="text-[10px] font-medium bg-background px-2 py-1 rounded-md border border-border capitalize">
                     🍎 {{ alert.food }}
                   </div>
                </div>

                <!-- Warning Recommendation -->
                <div v-if="alert.recommendation" class="mt-2 text-xs font-medium p-2 rounded bg-background/50 border border-border/50 text-foreground">
                  <span class="opacity-70">Action:</span> {{ alert.recommendation }}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
main::-webkit-scrollbar {
  display: none;
}
main {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
</style>
