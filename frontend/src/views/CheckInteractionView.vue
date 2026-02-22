<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Search, AlertTriangle, CheckCircle, Apple, Pill, Clock } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import AppNavbar from '@/components/common/AppNavbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import AnimatedBackground from '@/components/animations/AnimatedBackground.vue'
import { interactionApi, foodApi } from '@/services/api'
import { useMedicationsStore } from '@/stores/medications'
import { useInteractionHistoryStore } from '@/stores/interactionHistory'
import { useDebouncedFn } from '@/composables/useDebounce'
import { SEVERITY_CONFIG } from '@/constants'

const meds = useMedicationsStore()
const historyStore = useInteractionHistoryStore()

const foodQuery = ref('')
const foodResults = ref<any[]>([])
const selectedFood = ref('')
const searchingFood = ref(false)
const checking = ref(false)
const results = ref<any[]>([])
const hasChecked = ref(false)
const showClearDialog = ref(false)

onMounted(() => {
  meds.fetchMedications()
  historyStore.fetchHistory()
})

const debouncedFoodSearch = useDebouncedFn(async (query: string) => {
  if (query.length < 2) { foodResults.value = []; return }
  searchingFood.value = true
  try {
    const response = await foodApi.search(query)
    const foods = response.data?.data?.foods || response.data?.foods || []
    foodResults.value = foods.slice(0, 8).map((f: any) => ({
      fdcId: f.fdc_id || f.fdcId,
      description: f.description,
      category: f.brand_owner || f.data_type,
    }))
  } catch { foodResults.value = [] }
  finally { searchingFood.value = false }
}, 300)

watch(foodQuery, (val) => debouncedFoodSearch(val))

function selectFood(food: any) {
  selectedFood.value = food.description
  foodQuery.value = ''
  foodResults.value = []
}

async function checkInteractions() {
  if (!selectedFood.value || !meds.medications.length) return
  checking.value = true
  hasChecked.value = true
  results.value = []
  try {
    for (const med of meds.medications) {
      const { data } = await interactionApi.check(med.drugName, selectedFood.value)
      if (data.interaction) results.value.push(data.interaction)
    }
    await historyStore.saveCheck(
      selectedFood.value,
      meds.medications.map(m => m.drugName),
      results.value
    )
  } catch (err) { console.error(err) }
  finally { checking.value = false }
}

function reset() { selectedFood.value = ''; results.value = []; hasChecked.value = false }

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

function confirmClearHistory() {
  historyStore.clearHistory()
  showClearDialog.value = false
}
</script>

<template>
  <div class="h-screen flex flex-col overflow-hidden bg-background">
    <AnimatedBackground />
    <AppNavbar />
    <main class="flex-1 flex flex-col overflow-hidden mx-auto w-full max-w-3xl px-4 py-4 sm:px-6">

      <!-- Header -->
      <div class="mb-4 text-center">
        <h1 class="text-2xl font-bold text-gradient-animate">Check Interactions</h1>
        <p class="text-sm text-muted-foreground">Check if foods are safe with your medications</p>
      </div>

      <!-- No Medications Warning -->
      <Card v-if="!meds.medications.length" variant="gold" class="mb-4 bg-amber-500/5 backdrop-blur-md">
        <CardContent class="flex items-center gap-4 p-6">
          <Pill class="h-8 w-8 text-amber-600 dark:text-amber-400" />
          <div>
            <p class="font-semibold text-amber-700 dark:text-amber-300">No Medications Added</p>
            <p class="text-sm text-amber-600 dark:text-amber-400">Add your medications first to check for interactions</p>
          </div>
        </CardContent>
      </Card>

      <!-- Hero: Check Interaction Card -->
      <Card variant="gold" class="dialog-solid mb-4 bg-card/80 dark:bg-card/60 backdrop-blur-md shadow-md">
        <CardContent class="p-6">
          <!-- Food Search -->
          <div v-if="!selectedFood" class="space-y-3">
            <label class="text-sm font-medium">What are you eating?</label>
            <div class="relative">
              <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input v-model="foodQuery" placeholder="Search for a food..." class="pl-10" />
            </div>
            <LoadingSpinner v-if="searchingFood" size="sm" />
            <div v-else-if="foodResults.length" class="max-h-48 space-y-1 overflow-y-auto scrollbar-hide rounded-lg border border-border">
              <button
                v-for="food in foodResults"
                :key="food.fdcId"
                class="w-full rounded-lg border border-transparent px-4 py-3 text-left transition-all duration-200 hover:scale-[1.01] hover:border-teal-500/50 hover:bg-teal-500/10 cursor-pointer"
                @click="selectFood(food)"
              >
                <p class="font-medium text-foreground">{{ food.description }}</p>
                <p v-if="food.category" class="text-sm text-muted-foreground">{{ food.category }}</p>
              </button>
            </div>
          </div>

          <!-- Selected Food + Check Button -->
          <div v-else class="space-y-4">
            <div class="flex items-center gap-3 rounded-xl bg-cyan-500/10 p-4">
              <Apple class="h-6 w-6 text-cyan-600 dark:text-cyan-400" />
              <span class="flex-1 font-medium text-foreground">{{ selectedFood }}</span>
              <Button variant="outline" hover="lift" size="sm" @click="reset">Change</Button>
            </div>
            <div class="rounded-lg bg-muted/50 p-3">
              <p class="text-sm text-muted-foreground">Checking against {{ meds.medications.length }} medication(s)</p>
            </div>
            <Button variant="outline" hover="glow" class="mx-auto gap-2 border-2 border-gold" size="lg" :disabled="checking" @click="checkInteractions">
              <Search class="h-4 w-4" />{{ checking ? 'Checking...' : 'Check Interactions' }}
            </Button>

            <!-- Loader (inside card) -->
            <LoadingSpinner v-if="checking" size="sm" text="Checking interactions..." class="pt-2" />

            <!-- All Clear (inside card) -->
            <div v-else-if="hasChecked && !results.length" class="flex items-center gap-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 p-4">
              <CheckCircle class="h-6 w-6 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <div>
                <p class="font-semibold text-emerald-700 dark:text-emerald-300">All Clear!</p>
                <p class="text-sm text-emerald-600 dark:text-emerald-400">No known interactions found with your medications</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Interaction Results (outside card, only when there ARE interactions) -->
      <div v-if="hasChecked && results.length && !checking" class="mb-4 flex-1 overflow-y-auto scrollbar-hide space-y-3">
        <Card
          v-for="result in results"
          :key="`${result.drugName}-${result.foodName}`"
          variant="gold"
          :class="['bg-card/80 dark:bg-card/60 backdrop-blur-md shadow-md transition-colors duration-200 hover:bg-teal-500/5', SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG].borderClass]"
        >
          <CardHeader class="pb-2">
            <div class="flex items-center gap-2">
              <AlertTriangle :class="['h-5 w-5', SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG].textClass]" />
              <CardTitle class="text-lg">{{ result.drugName }}</CardTitle>
              <span :class="['ml-auto rounded-full px-2.5 py-0.5 text-xs font-medium', SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG].bgClass, SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG].textClass]">
                {{ SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG].label }}
              </span>
            </div>
          </CardHeader>
          <CardContent>
            <p class="text-muted-foreground">{{ result.effect }}</p>
            <div class="mt-3 rounded-lg bg-muted/50 p-3">
              <p class="text-sm font-medium text-foreground">Recommendation</p>
              <p class="text-sm text-muted-foreground">{{ result.recommendation }}</p>
            </div>
          </CardContent>
        </Card>
      </div>

    </main>

    <!-- History: Full-width, pinned to bottom -->
    <div v-if="historyStore.history.length" class="border-t border-border/30 px-4 py-3 sm:px-6">
      <div class="flex items-center justify-between mb-3">
        <p class="text-sm font-semibold underline text-muted-foreground">Recent Checks</p>
        <Button variant="ghost" size="sm" class="text-xs text-muted-foreground" @click="showClearDialog = true">Clear All</Button>
      </div>
      <div class="flex gap-3 overflow-x-auto scrollbar-hide pb-2">
        <div
          v-for="entry in historyStore.history"
          :key="entry.id"
          :class="[
            'flex-shrink-0 w-44 rounded-xl border bg-card p-3 transition-colors duration-200 hover:bg-teal-500/5 cursor-pointer',
            entry.had_interaction ? 'border-amber-500/30' : 'border-emerald-500/30'
          ]"
        >
          <div class="flex items-center gap-2 mb-1.5">
            <AlertTriangle v-if="entry.had_interaction" class="h-3.5 w-3.5 text-amber-500 shrink-0" />
            <CheckCircle v-else class="h-3.5 w-3.5 text-emerald-500 shrink-0" />
            <p class="text-sm font-medium text-foreground truncate">{{ entry.food_name }}</p>
          </div>
          <p class="text-xs text-muted-foreground mb-1">
            {{ entry.had_interaction ? `${entry.interaction_count} interaction(s)` : 'No interactions' }}
          </p>
          <div class="flex items-center gap-1 text-xs text-muted-foreground/60">
            <Clock class="h-3 w-3" />
            {{ formatDate(entry.created_at) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Clear History Confirmation -->
    <ConfirmDialog
      v-model:open="showClearDialog"
      title="Clear History"
      description="Are you sure you want to clear all interaction check history? This action cannot be undone."
      confirm-label="Clear All"
      variant="destructive"
      @confirm="confirmClearHistory"
    />
  </div>
</template>
