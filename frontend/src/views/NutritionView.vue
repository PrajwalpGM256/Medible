<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search, Apple, Flame, Beef, Wheat, Droplets } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import AppNavbar from '@/components/common/AppNavbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { foodApi } from '@/services/api'
import { useDebouncedFn } from '@/composables/useDebounce'

const searchQuery = ref('')
const searchResults = ref<any[]>([])
const selectedFood = ref<any>(null)
const searching = ref(false)
const loadingDetails = ref(false)

const debouncedSearch = useDebouncedFn(async (query: string) => {
  if (query.length < 2) { searchResults.value = []; return }
  searching.value = true
  try {
    const response = await foodApi.search(query)
    const foods = response.data?.data?.foods || response.data?.foods || []
    searchResults.value = foods.slice(0, 10).map((f: any) => ({
      fdcId: f.fdc_id || f.fdcId,
      description: f.description,
      brandOwner: f.brand_owner || f.brandOwner || 'Generic',
      dataType: f.data_type || f.dataType,
      nutrients: f.nutrients || {},
      servingSize: f.serving_size || f.servingSize,
      servingUnit: f.serving_unit || f.servingUnit || 'g',
    }))
  } catch { searchResults.value = [] }
  finally { searching.value = false }
}, 300)

watch(searchQuery, (val) => debouncedSearch(val))

function selectFood(food: any) {
  selectedFood.value = food
  searchQuery.value = ''
  searchResults.value = []
}

function clearSelection() {
  selectedFood.value = null
}

function formatNumber(val: any): string {
  if (val === null || val === undefined) return '0'
  return Number(val).toFixed(1)
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <AppNavbar />
    <main class="mx-auto max-w-2xl px-4 py-6 sm:px-6 sm:py-8">
      <div class="mb-6 text-center">
        <h1 class="text-2xl font-bold text-foreground">Food Nutrition</h1>
        <p class="text-muted-foreground">Look up nutritional information for any food</p>
      </div>

      <!-- Search -->
      <Card class="mb-6">
        <CardContent class="p-6">
          <div v-if="!selectedFood" class="space-y-3">
            <label class="text-sm font-medium">Search for a food</label>
            <div class="relative">
              <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input v-model="searchQuery" placeholder="e.g., chicken breast, banana, rice..." class="pl-10" />
            </div>
            <LoadingSpinner v-if="searching" size="sm" />
            <div v-else-if="searchResults.length" class="max-h-64 space-y-1 overflow-y-auto rounded-lg border border-border">
              <button v-for="food in searchResults" :key="food.fdcId" class="w-full px-4 py-3 text-left hover:bg-accent transition-colors" @click="selectFood(food)">
                <p class="font-medium text-foreground">{{ food.description }}</p>
                <p class="text-sm text-muted-foreground">{{ food.brandOwner }}</p>
              </button>
            </div>
            <p v-else-if="searchQuery.length >= 2 && !searching" class="text-sm text-muted-foreground text-center py-4">
              No foods found. Try a different search term.
            </p>
          </div>

          <!-- Selected Food Header -->
          <div v-else class="space-y-4">
            <div class="flex items-center gap-3 rounded-xl bg-emerald-500/10 p-4">
              <Apple class="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
              <div class="flex-1">
                <p class="font-semibold text-foreground">{{ selectedFood.description }}</p>
                <p class="text-sm text-muted-foreground">{{ selectedFood.brandOwner }}</p>
              </div>
              <Button variant="ghost" size="sm" @click="clearSelection">Change</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Nutrition Info -->
      <div v-if="selectedFood" class="space-y-4">
        <!-- Serving Size -->
        <Card>
          <CardContent class="p-4">
            <p class="text-sm text-muted-foreground">Serving Size</p>
            <p class="text-lg font-semibold text-foreground">
              {{ selectedFood.servingSize || 100 }}{{ selectedFood.servingUnit || 'g' }}
            </p>
          </CardContent>
        </Card>

        <!-- Macros -->
        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-lg">Macronutrients</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <!-- Calories -->
            <div class="flex items-center gap-4 rounded-lg bg-orange-500/10 p-4">
              <div class="rounded-full bg-orange-500/20 p-2">
                <Flame class="h-5 w-5 text-orange-600 dark:text-orange-400" />
              </div>
              <div class="flex-1">
                <p class="text-sm text-muted-foreground">Calories</p>
                <p class="text-xl font-bold text-foreground">{{ formatNumber(selectedFood.nutrients?.calories) }} kcal</p>
              </div>
            </div>

            <div class="grid grid-cols-3 gap-3">
              <!-- Protein -->
              <div class="rounded-lg bg-red-500/10 p-4 text-center">
                <Beef class="mx-auto h-5 w-5 text-red-600 dark:text-red-400 mb-1" />
                <p class="text-xs text-muted-foreground">Protein</p>
                <p class="text-lg font-bold text-foreground">{{ formatNumber(selectedFood.nutrients?.protein) }}g</p>
              </div>

              <!-- Carbs -->
              <div class="rounded-lg bg-amber-500/10 p-4 text-center">
                <Wheat class="mx-auto h-5 w-5 text-amber-600 dark:text-amber-400 mb-1" />
                <p class="text-xs text-muted-foreground">Carbs</p>
                <p class="text-lg font-bold text-foreground">{{ formatNumber(selectedFood.nutrients?.carbs) }}g</p>
              </div>

              <!-- Fat -->
              <div class="rounded-lg bg-yellow-500/10 p-4 text-center">
                <Droplets class="mx-auto h-5 w-5 text-yellow-600 dark:text-yellow-400 mb-1" />
                <p class="text-xs text-muted-foreground">Fat</p>
                <p class="text-lg font-bold text-foreground">{{ formatNumber(selectedFood.nutrients?.fat) }}g</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Additional Nutrients -->
        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-lg">Other Nutrients</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-2 gap-3">
              <div class="flex justify-between rounded-lg border border-border p-3">
                <span class="text-muted-foreground">Fiber</span>
                <span class="font-medium text-foreground">{{ formatNumber(selectedFood.nutrients?.fiber) }}g</span>
              </div>
              <div class="flex justify-between rounded-lg border border-border p-3">
                <span class="text-muted-foreground">Sugar</span>
                <span class="font-medium text-foreground">{{ formatNumber(selectedFood.nutrients?.sugar) }}g</span>
              </div>
              <div class="flex justify-between rounded-lg border border-border p-3">
                <span class="text-muted-foreground">Sodium</span>
                <span class="font-medium text-foreground">{{ formatNumber(selectedFood.nutrients?.sodium) }}mg</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Data Source -->
        <p class="text-center text-xs text-muted-foreground">
          Data from USDA FoodData Central
        </p>
      </div>

      <!-- Empty State -->
      <div v-else-if="!searchQuery" class="py-12 text-center">
        <Apple class="mx-auto h-12 w-12 text-muted-foreground/50" />
        <p class="mt-4 text-lg font-medium text-foreground">Search for a food</p>
        <p class="mt-1 text-muted-foreground">Enter a food name above to see its nutritional information</p>
      </div>
    </main>
  </div>
</template>
