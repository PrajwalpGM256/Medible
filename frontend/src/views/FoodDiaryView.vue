<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Search, Plus, Trash2, Apple, Flame, Beef, Wheat, Droplets, Calendar, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import AppNavbar from '@/components/common/AppNavbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { foodApi, foodDiaryApi } from '@/services/api'
import { useDebouncedFn } from '@/composables/useDebounce'

// State
const loading = ref(false)
const todayLogs = ref<any[]>([])
const todayTotals = ref({ calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0, sugar: 0, sodium: 0, food_count: 0 })
const byMeal = ref<Record<string, any[]>>({ breakfast: [], lunch: [], dinner: [], snack: [], other: [] })

// Add food state
const showAddFood = ref(false)
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const searching = ref(false)
const selectedFood = ref<any>(null)
const servings = ref(1)
const mealType = ref('snack')
const notes = ref('')
const adding = ref(false)

// Date navigation
const currentDate = ref(new Date())
const formattedDate = computed(() => currentDate.value.toISOString().split('T')[0])
const displayDate = computed(() => {
  const today = new Date()
  const date = currentDate.value
  if (date.toDateString() === today.toDateString()) return 'Today'
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) return 'Yesterday'
  return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
})

const mealTypes = [
  { value: 'breakfast', label: '🌅 Breakfast' },
  { value: 'lunch', label: '☀️ Lunch' },
  { value: 'dinner', label: '🌙 Dinner' },
  { value: 'snack', label: '🍿 Snack' },
]

onMounted(() => fetchLogs())

watch(currentDate, () => fetchLogs())

async function fetchLogs() {
  loading.value = true
  try {
    const { data } = await foodDiaryApi.getByDate(formattedDate.value)
    const result = data.data
    todayLogs.value = result.logs || []
    todayTotals.value = result.totals || { calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0, sugar: 0, sodium: 0, food_count: 0 }
    
    // Group by meal
    byMeal.value = { breakfast: [], lunch: [], dinner: [], snack: [], other: [] }
    for (const log of todayLogs.value) {
      const meal = log.meal_type || 'other'
      if (byMeal.value[meal]) {
        byMeal.value[meal].push(log)
      } else {
        byMeal.value.other.push(log)
      }
    }
  } catch (err) {
    console.error('Failed to fetch food logs:', err)
  } finally {
    loading.value = false
  }
}

const debouncedSearch = useDebouncedFn(async (query: string) => {
  if (query.length < 2) { searchResults.value = []; return }
  searching.value = true
  try {
    const response = await foodApi.search(query)
    const foods = response.data?.data?.foods || response.data?.foods || []
    searchResults.value = foods.slice(0, 8).map((f: any) => ({
      fdcId: f.fdc_id || f.fdcId,
      description: f.description,
      brandOwner: f.brand_owner || f.brandOwner || 'Generic',
      nutrients: f.nutrients || {},
      servingSize: f.serving_size || f.servingSize || 100,
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
  servings.value = 1
  notes.value = ''
}

async function addFoodLog() {
  if (!selectedFood.value) return
  adding.value = true
  try {
    const nutrients = selectedFood.value.nutrients || {}
    await foodDiaryApi.add({
      food_name: selectedFood.value.description,
      fdc_id: selectedFood.value.fdcId,
      brand_owner: selectedFood.value.brandOwner,
      servings: servings.value,
      serving_size: selectedFood.value.servingSize,
      serving_unit: selectedFood.value.servingUnit,
      calories: (nutrients.calories || 0) * servings.value,
      protein: (nutrients.protein || 0) * servings.value,
      carbs: (nutrients.carbs || 0) * servings.value,
      fat: (nutrients.fat || 0) * servings.value,
      fiber: (nutrients.fiber || 0) * servings.value,
      sugar: (nutrients.sugar || 0) * servings.value,
      sodium: (nutrients.sodium || 0) * servings.value,
      meal_type: mealType.value,
      notes: notes.value || undefined,
      logged_date: formattedDate.value,
    })
    clearSelection()
    showAddFood.value = false
    await fetchLogs()
  } catch (err) {
    console.error('Failed to add food:', err)
  } finally {
    adding.value = false
  }
}

async function deleteLog(id: number) {
  try {
    await foodDiaryApi.remove(id)
    await fetchLogs()
  } catch (err) {
    console.error('Failed to delete:', err)
  }
}

function prevDay() {
  const newDate = new Date(currentDate.value)
  newDate.setDate(newDate.getDate() - 1)
  currentDate.value = newDate
}

function nextDay() {
  const newDate = new Date(currentDate.value)
  newDate.setDate(newDate.getDate() + 1)
  if (newDate <= new Date()) {
    currentDate.value = newDate
  }
}

function goToToday() {
  currentDate.value = new Date()
}

function formatNum(val: any): string {
  if (val === null || val === undefined) return '0'
  return Math.round(Number(val)).toString()
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <AppNavbar />
    <main class="mx-auto max-w-2xl px-4 py-6 sm:px-6 sm:py-8">
      <!-- Header -->
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-foreground">Food Diary</h1>
          <p class="text-muted-foreground">Track what you eat daily</p>
        </div>
        <Button @click="showAddFood = true" class="gap-2">
          <Plus class="h-4 w-4" /> Log Food
        </Button>
      </div>

      <!-- Date Navigation -->
      <Card class="mb-6">
        <CardContent class="flex items-center justify-between p-4">
          <Button variant="ghost" size="icon" @click="prevDay">
            <ChevronLeft class="h-5 w-5" />
          </Button>
          <div class="flex items-center gap-2 text-center">
            <Calendar class="h-5 w-5 text-muted-foreground" />
            <span class="font-semibold text-foreground">{{ displayDate }}</span>
            <button v-if="displayDate !== 'Today'" @click="goToToday" class="ml-2 text-xs text-primary hover:underline">
              Go to today
            </button>
          </div>
          <Button variant="ghost" size="icon" @click="nextDay" :disabled="displayDate === 'Today'">
            <ChevronRight class="h-5 w-5" />
          </Button>
        </CardContent>
      </Card>

      <!-- Daily Summary -->
      <Card class="mb-6">
        <CardHeader class="pb-2">
          <CardTitle class="text-lg">Daily Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-4 gap-3">
            <div class="rounded-lg bg-orange-500/10 p-3 text-center">
              <Flame class="mx-auto h-5 w-5 text-orange-600 dark:text-orange-400" />
              <p class="text-xl font-bold text-foreground">{{ formatNum(todayTotals.calories) }}</p>
              <p class="text-xs text-muted-foreground">Calories</p>
            </div>
            <div class="rounded-lg bg-red-500/10 p-3 text-center">
              <Beef class="mx-auto h-5 w-5 text-red-600 dark:text-red-400" />
              <p class="text-xl font-bold text-foreground">{{ formatNum(todayTotals.protein) }}g</p>
              <p class="text-xs text-muted-foreground">Protein</p>
            </div>
            <div class="rounded-lg bg-amber-500/10 p-3 text-center">
              <Wheat class="mx-auto h-5 w-5 text-amber-600 dark:text-amber-400" />
              <p class="text-xl font-bold text-foreground">{{ formatNum(todayTotals.carbs) }}g</p>
              <p class="text-xs text-muted-foreground">Carbs</p>
            </div>
            <div class="rounded-lg bg-yellow-500/10 p-3 text-center">
              <Droplets class="mx-auto h-5 w-5 text-yellow-600 dark:text-yellow-400" />
              <p class="text-xl font-bold text-foreground">{{ formatNum(todayTotals.fat) }}g</p>
              <p class="text-xs text-muted-foreground">Fat</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Food Logs -->
      <LoadingSpinner v-if="loading" class="py-8" />
      <div v-else-if="!todayLogs.length" class="py-12 text-center">
        <Apple class="mx-auto h-12 w-12 text-muted-foreground/50" />
        <p class="mt-4 text-lg font-medium text-foreground">No foods logged</p>
        <p class="mt-1 text-muted-foreground">Tap "Log Food" to start tracking</p>
      </div>
      <Tabs v-else default-value="all" class="w-full">
        <TabsList class="mb-4 w-full">
          <TabsTrigger value="all" class="flex-1">All ({{ todayLogs.length }})</TabsTrigger>
          <TabsTrigger v-for="meal in mealTypes" :key="meal.value" :value="meal.value" class="flex-1">
            {{ meal.label.split(' ')[0] }} ({{ byMeal[meal.value]?.length || 0 }})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          <div class="space-y-3">
            <Card v-for="log in todayLogs" :key="log.id">
              <CardContent class="flex items-center gap-4 p-4">
                <div class="rounded-full bg-emerald-500/10 p-2">
                  <Apple class="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-foreground truncate">{{ log.food_name }}</p>
                  <p class="text-sm text-muted-foreground">
                    {{ formatNum(log.calories) }} cal · {{ log.servings || 1 }} serving(s)
                  </p>
                </div>
                <Button variant="ghost" size="icon" class="text-destructive hover:bg-destructive/10" @click="deleteLog(log.id)">
                  <Trash2 class="h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent v-for="meal in mealTypes" :key="meal.value" :value="meal.value">
          <div v-if="byMeal[meal.value]?.length" class="space-y-3">
            <Card v-for="log in byMeal[meal.value]" :key="log.id">
              <CardContent class="flex items-center gap-4 p-4">
                <div class="rounded-full bg-emerald-500/10 p-2">
                  <Apple class="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-foreground truncate">{{ log.food_name }}</p>
                  <p class="text-sm text-muted-foreground">{{ formatNum(log.calories) }} cal</p>
                </div>
                <Button variant="ghost" size="icon" class="text-destructive" @click="deleteLog(log.id)">
                  <Trash2 class="h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          </div>
          <p v-else class="py-8 text-center text-muted-foreground">No {{ meal.label.split(' ')[1].toLowerCase() }} logged</p>
        </TabsContent>
      </Tabs>

      <!-- Add Food Modal -->
      <div v-if="showAddFood" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/50 p-4" @click.self="showAddFood = false">
        <Card class="w-full max-w-lg max-h-[90vh] overflow-y-auto">
          <CardHeader>
            <CardTitle>Log Food</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <!-- Search -->
            <div v-if="!selectedFood">
              <label class="text-sm font-medium">Search food</label>
              <div class="relative mt-1">
                <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input v-model="searchQuery" placeholder="e.g., chicken, rice, apple..." class="pl-10" />
              </div>
              <LoadingSpinner v-if="searching" size="sm" class="mt-2" />
              <div v-else-if="searchResults.length" class="mt-2 max-h-48 space-y-1 overflow-y-auto rounded-lg border border-border">
                <button v-for="food in searchResults" :key="food.fdcId" class="w-full px-4 py-3 text-left hover:bg-accent" @click="selectFood(food)">
                  <p class="font-medium text-foreground">{{ food.description }}</p>
                  <p class="text-sm text-muted-foreground">{{ food.brandOwner }} · {{ food.nutrients?.calories || 0 }} cal</p>
                </button>
              </div>
            </div>

            <!-- Selected Food -->
            <div v-else class="space-y-4">
              <div class="flex items-center gap-3 rounded-xl bg-emerald-500/10 p-4">
                <Apple class="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
                <div class="flex-1">
                  <p class="font-semibold text-foreground">{{ selectedFood.description }}</p>
                  <p class="text-sm text-muted-foreground">{{ selectedFood.nutrients?.calories || 0 }} cal per serving</p>
                </div>
                <Button variant="ghost" size="sm" @click="clearSelection">Change</Button>
              </div>

              <!-- Servings -->
              <div>
                <label class="text-sm font-medium">Servings</label>
                <Input v-model.number="servings" type="number" min="0.25" step="0.25" class="mt-1" />
              </div>

              <!-- Meal Type -->
              <div>
                <label class="text-sm font-medium">Meal</label>
                <div class="mt-1 grid grid-cols-4 gap-2">
                  <button
                    v-for="meal in mealTypes"
                    :key="meal.value"
                    :class="['rounded-lg border p-2 text-center text-sm transition-colors', mealType === meal.value ? 'border-primary bg-primary/10 text-primary' : 'border-border hover:bg-accent']"
                    @click="mealType = meal.value"
                  >
                    {{ meal.label }}
                  </button>
                </div>
              </div>

              <!-- Notes -->
              <div>
                <label class="text-sm font-medium">Notes (optional)</label>
                <Input v-model="notes" placeholder="e.g., with salad..." class="mt-1" />
              </div>

              <!-- Nutrition Preview -->
              <div class="rounded-lg bg-muted/50 p-3">
                <p class="text-sm font-medium text-foreground mb-2">Nutrition ({{ servings }} serving{{ servings !== 1 ? 's' : '' }})</p>
                <div class="grid grid-cols-4 gap-2 text-center text-sm">
                  <div><p class="font-bold text-foreground">{{ formatNum((selectedFood.nutrients?.calories || 0) * servings) }}</p><p class="text-xs text-muted-foreground">cal</p></div>
                  <div><p class="font-bold text-foreground">{{ formatNum((selectedFood.nutrients?.protein || 0) * servings) }}g</p><p class="text-xs text-muted-foreground">protein</p></div>
                  <div><p class="font-bold text-foreground">{{ formatNum((selectedFood.nutrients?.carbs || 0) * servings) }}g</p><p class="text-xs text-muted-foreground">carbs</p></div>
                  <div><p class="font-bold text-foreground">{{ formatNum((selectedFood.nutrients?.fat || 0) * servings) }}g</p><p class="text-xs text-muted-foreground">fat</p></div>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex gap-3 pt-2">
              <Button variant="outline" class="flex-1" @click="showAddFood = false">Cancel</Button>
              <Button class="flex-1" :disabled="!selectedFood || adding" @click="addFoodLog">
                {{ adding ? 'Adding...' : 'Add Food' }}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  </div>
</template>
