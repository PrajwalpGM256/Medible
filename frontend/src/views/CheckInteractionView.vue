<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Search, AlertTriangle, CheckCircle, Apple, Pill } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import AppNavbar from '@/components/common/AppNavbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { interactionApi, foodApi } from '@/services/api'
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

onMounted(() => { if (!meds.medications.length) meds.fetchMedications() })

const debouncedFoodSearch = useDebouncedFn(async (query: string) => {
  if (query.length < 2) { foodResults.value = []; return }
  searchingFood.value = true
  try {
    const response = await foodApi.search(query)
    // Backend returns { data: { foods: [...] } }
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
  } catch (err) { console.error(err) }
  finally { checking.value = false }
}

function reset() { selectedFood.value = ''; results.value = []; hasChecked.value = false }
</script>

<template>
  <div class="min-h-screen bg-background">
    <AppNavbar />
    <main class="mx-auto max-w-2xl px-4 py-6 sm:px-6 sm:py-8">
      <div class="mb-6 text-center">
        <h1 class="text-2xl font-bold text-foreground">Check Food Safety</h1>
        <p class="text-muted-foreground">See if a food is safe with your medications</p>
      </div>
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
    </main>
  </div>
</template>
