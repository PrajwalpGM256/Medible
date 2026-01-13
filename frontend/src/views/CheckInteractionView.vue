<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Search, AlertTriangle, CheckCircle, Apple, Pill, History, Clock, Trash2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import AppNavbar from '@/components/common/AppNavbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { interactionApi, foodApi, interactionHistoryApi } from '@/services/api'
import { useMedicationsStore } from '@/stores/medications'
import { useDebouncedFn } from '@/composables/useDebounce'
import { SEVERITY_CONFIG } from '@/constants'

const meds = useMedicationsStore()

const foodQuery = ref('')
const foodResults = ref<any[]>([])
const selectedFood = ref('')
const searchingFood = ref(false)
const checking = ref(false)
const results = ref<any[]>([])
const hasChecked = ref(false)

// Check history from database
const checkHistory = ref<any[]>([])
const loadingHistory = ref(false)

onMounted(() => { 
  if (!meds.medications.length) meds.fetchMedications()
  loadHistory()
})

async function loadHistory() {
  loadingHistory.value = true
  try {
    const { data } = await interactionHistoryApi.getAll(50)
    checkHistory.value = data.data?.history || []
  } catch (err) {
    console.error('Failed to load history:', err)
    checkHistory.value = []
  } finally {
    loadingHistory.value = false
  }
}

async function saveToHistory(food: string, interactions: any[]) {
  try {
    await interactionHistoryApi.save({
      food_name: food,
      medications: meds.medications.map(m => m.drugName),
      interactions: interactions,
    })
    // Reload history to get the new entry
    await loadHistory()
  } catch (err) {
    console.error('Failed to save to history:', err)
  }
}

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
    saveToHistory(selectedFood.value, results.value)
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

async function clearHistory() {
  try {
    await interactionHistoryApi.clear()
    checkHistory.value = []
  } catch (err) {
    console.error('Failed to clear history:', err)
  }
}

async function deleteHistoryItem(id: number) {
  try {
    await interactionHistoryApi.delete(id)
    checkHistory.value = checkHistory.value.filter(h => h.id !== id)
  } catch (err) {
    console.error('Failed to delete history item:', err)
  }
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <AppNavbar />
    <main class="mx-auto max-w-2xl px-4 py-6 sm:px-6 sm:py-8">
      <div class="mb-6 text-center">
        <h1 class="text-2xl font-bold text-foreground">Check Interactions</h1>
        <p class="text-muted-foreground">Check if foods are safe with your medications</p>
      </div>

      <Tabs default-value="check" class="w-full">
        <TabsList class="mb-6 w-full">
          <TabsTrigger value="check" class="flex-1 gap-2">
            <Search class="h-4 w-4" /> Check Food
          </TabsTrigger>
          <TabsTrigger value="history" class="flex-1 gap-2">
            <History class="h-4 w-4" /> History ({{ checkHistory.length }})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="check">
          <Card class="mb-6">
            <CardContent class="p-6">
              <div v-if="!selectedFood" class="space-y-3">
                <label class="text-sm font-medium">What are you eating?</label>
                <div class="relative">
                  <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input v-model="foodQuery" placeholder="Search for a food..." class="pl-10" />
                </div>
                <LoadingSpinner v-if="searchingFood" size="sm" />
                <div v-else-if="foodResults.length" class="max-h-48 space-y-1 overflow-y-auto rounded-lg border border-border">
                  <button v-for="food in foodResults" :key="food.fdcId" class="w-full px-4 py-3 text-left hover:bg-accent" @click="selectFood(food)">
                    <p class="font-medium text-foreground">{{ food.description }}</p>
                    <p v-if="food.category" class="text-sm text-muted-foreground">{{ food.category }}</p>
                  </button>
                </div>
              </div>
              <div v-else class="space-y-4">
                <div class="flex items-center gap-3 rounded-xl bg-cyan-500/10 p-4">
                  <Apple class="h-6 w-6 text-cyan-600 dark:text-cyan-400" />
                  <span class="flex-1 font-medium text-foreground">{{ selectedFood }}</span>
                  <Button variant="ghost" size="sm" @click="reset">Change</Button>
                </div>
                <div class="rounded-lg bg-muted/50 p-3">
                  <p class="text-sm text-muted-foreground">Checking against {{ meds.medications.length }} medication(s)</p>
                </div>
                <Button class="w-full gap-2" size="lg" :disabled="checking" @click="checkInteractions">
                  <Search class="h-4 w-4" />{{ checking ? 'Checking...' : 'Check Interactions' }}
                </Button>
              </div>
            </CardContent>
          </Card>
          
          <div v-if="checking" class="py-8"><LoadingSpinner text="Checking interactions..." /></div>
          <div v-else-if="hasChecked">
            <Card v-if="!results.length" class="border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-950">
              <CardContent class="flex items-center gap-4 p-6">
                <CheckCircle class="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
                <div>
                  <p class="font-semibold text-emerald-700 dark:text-emerald-300">All Clear!</p>
                  <p class="text-sm text-emerald-600 dark:text-emerald-400">No known interactions found with your medications</p>
                </div>
              </CardContent>
            </Card>
            <div v-else class="space-y-4">
              <Card v-for="result in results" :key="`${result.drugName}-${result.foodName}`" :class="SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG].borderClass">
                <CardHeader class="pb-2">
                  <div class="flex items-center gap-2">
                    <AlertTriangle :class="['h-5 w-5', SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG].textClass]" />
                    <CardTitle class="text-lg">{{ result.drugName }}</CardTitle>
                    <span :class="['ml-auto rounded-full px-2.5 py-0.5 text-xs font-medium', SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG].bgClass, SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG].textClass]">{{ SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG].label }}</span>
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
          </div>
          
          <Card v-if="!meds.medications.length" class="border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950">
            <CardContent class="flex items-center gap-4 p-6">
              <Pill class="h-8 w-8 text-amber-600 dark:text-amber-400" />
              <div>
                <p class="font-semibold text-amber-700 dark:text-amber-300">No Medications Added</p>
                <p class="text-sm text-amber-600 dark:text-amber-400">Add your medications first to check for interactions</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history">
          <LoadingSpinner v-if="loadingHistory" text="Loading history..." />
          <div v-else-if="!checkHistory.length" class="py-12 text-center">
            <History class="mx-auto h-12 w-12 text-muted-foreground/50" />
            <p class="mt-4 text-lg font-medium text-foreground">No check history</p>
            <p class="mt-1 text-muted-foreground">Your food interaction checks will appear here</p>
          </div>
          <div v-else class="space-y-3">
            <div class="flex items-center justify-between mb-4">
              <p class="text-sm text-muted-foreground">Recent checks ({{ checkHistory.length }})</p>
              <Button variant="ghost" size="sm" @click="clearHistory">Clear All</Button>
            </div>
            <Card v-for="entry in checkHistory" :key="entry.id" :class="entry.had_interaction ? 'border-amber-200 dark:border-amber-800' : 'border-emerald-200 dark:border-emerald-800'">
              <CardContent class="flex items-center gap-4 p-4">
                <div :class="['rounded-full p-2', entry.had_interaction ? 'bg-amber-500/10' : 'bg-emerald-500/10']">
                  <AlertTriangle v-if="entry.had_interaction" class="h-5 w-5 text-amber-600 dark:text-amber-400" />
                  <CheckCircle v-else class="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2">
                    <p class="font-medium text-foreground truncate">{{ entry.food_name }}</p>
                    <span v-if="entry.max_severity" :class="['rounded-full px-2 py-0.5 text-xs font-medium', SEVERITY_CONFIG[entry.max_severity as keyof typeof SEVERITY_CONFIG]?.bgClass, SEVERITY_CONFIG[entry.max_severity as keyof typeof SEVERITY_CONFIG]?.textClass]">
                      {{ SEVERITY_CONFIG[entry.max_severity as keyof typeof SEVERITY_CONFIG]?.label }}
                    </span>
                  </div>
                  <p class="text-sm text-muted-foreground">
                    {{ entry.had_interaction ? `${entry.interaction_count} interaction(s) found` : 'No interactions' }}
                    · {{ entry.medications_checked?.length || 0 }} medication(s) checked
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <div class="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock class="h-3 w-3" />
                    {{ formatDate(entry.checked_at) }}
                  </div>
                  <Button variant="ghost" size="icon" class="h-8 w-8 text-muted-foreground hover:text-destructive" @click="deleteHistoryItem(entry.id)">
                    <Trash2 class="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </main>
  </div>
</template>
