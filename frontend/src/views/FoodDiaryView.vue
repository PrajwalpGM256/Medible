<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import {
  Search, Plus, Apple, Flame, Beef, Wheat, Droplets,
  Calendar, ChevronLeft, ChevronRight, ChevronDown,
} from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent } from '@/components/ui/Card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import AppNavbar from '@/components/common/AppNavbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import AnimatedBackground from '@/components/animations/AnimatedBackground.vue'
import { foodApi, foodDiaryApi } from '@/services/api'
import { useDebouncedFn } from '@/composables/useDebounce'

// ── State ──
const loading = ref(false)
const todayLogs = ref<any[]>([])
const todayTotals = ref({
  calories: 0, protein: 0, carbs: 0, fat: 0,
  fiber: 0, sugar: 0, sodium: 0, food_count: 0,
})
const byMeal = ref<Record<string, any[]>>({
  breakfast: [], lunch: [], dinner: [], snack: [], other: [],
})

// Add food
const showAddFood = ref(false)
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const searching = ref(false)
const selectedFood = ref<any>(null)
const servings = ref(1)
const mealType = ref('snack')
const notes = ref('')
const adding = ref(false)

// Delete
const deletingLog = ref<any>(null)
const showDeleteDialog = ref(false)

// Date nav
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

const MEAL_TYPES = [
  { value: 'breakfast', label: '🌅 Breakfast' },
  { value: 'lunch', label: '☀️ Lunch' },
  { value: 'dinner', label: '🌙 Dinner' },
  { value: 'snack', label: '🍿 Snack' },
] as const

const mealOpenState = ref<Record<string, boolean>>({
  breakfast: false,
  lunch: false,
  dinner: false,
  snack: false,
  other: false,
})

function toggleMeal(meal: string) {
  mealOpenState.value[meal] = !mealOpenState.value[meal]
}

// ── Lifecycle ──
onMounted(() => fetchLogs())
watch(currentDate, () => fetchLogs())

// ── API ──
async function fetchLogs() {
  loading.value = true
  try {
    const { data } = await foodDiaryApi.getByDate(formattedDate.value)
    const result = data.data
    todayLogs.value = result.logs || []
    todayTotals.value = result.totals || {
      calories: 0, protein: 0, carbs: 0, fat: 0,
      fiber: 0, sugar: 0, sodium: 0, food_count: 0,
    }
    byMeal.value = { breakfast: [], lunch: [], dinner: [], snack: [], other: [] }
    for (const log of todayLogs.value) {
      const meal = log.meal_type || 'other'
      if (byMeal.value[meal]) byMeal.value[meal].push(log)
      else byMeal.value.other.push(log)
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
  mealType.value = 'snack'
}

function closeAddDialog() {
  showAddFood.value = false
  clearSelection()
  searchQuery.value = ''
  searchResults.value = []
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
    closeAddDialog()
    await fetchLogs()
  } catch (err) {
    console.error('Failed to add food:', err)
  } finally {
    adding.value = false
  }
}

function promptDelete(log: any) {
  deletingLog.value = log
  showDeleteDialog.value = true
}

async function confirmDelete() {
  if (!deletingLog.value) return
  try {
    await foodDiaryApi.remove(deletingLog.value.id)
    await fetchLogs()
  } catch (err) {
    console.error('Failed to delete:', err)
  }
  deletingLog.value = null
}

function prevDay() {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() - 1)
  currentDate.value = d
}

function nextDay() {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() + 1)
  if (d <= new Date()) currentDate.value = d
}

function goToToday() { currentDate.value = new Date() }

function fmt(val: any): string {
  if (val === null || val === undefined) return '0'
  return Math.round(Number(val)).toString()
}

function fmtDecimal(val: any): string {
  if (val === null || val === undefined) return '0'
  return Number(val).toFixed(1)
}
</script>

<template>
  <div class="h-screen flex flex-col overflow-hidden bg-background">
    <AnimatedBackground />
    <AppNavbar />
    <main class="flex-1 flex flex-col overflow-hidden mx-auto w-full max-w-7xl px-4 py-4 sm:px-6">

      <!-- Header Row (Title, Date Nav, Log Button) -->
      <div class="mb-6 flex items-center justify-between gap-4">
        <div class="w-1/3">
          <h1 class="text-2xl font-bold text-gradient-animate">Food & Nutrition</h1>
          <p class="text-sm text-muted-foreground">Track what you eat and explore nutritional info</p>
        </div>

        <!-- Date Nav centered -->
        <div class="flex items-center justify-between w-[320px] bg-card/80 dark:bg-card/60 backdrop-blur-md rounded-xl border-2 border-gold px-4 py-2 shadow-sm shrink-0">
          <Button variant="ghost" size="icon" class="h-8 w-8 rounded-lg shrink-0 hover:bg-gold/20" @click="prevDay">
            <ChevronLeft class="h-5 w-5" />
          </Button>
          <div class="flex items-center gap-2 justify-center text-sm">
            <Calendar class="h-4 w-4 text-muted-foreground" />
            <span class="font-semibold text-foreground">{{ displayDate }}</span>
          </div>
          <Button variant="ghost" size="icon" class="h-8 w-8 rounded-lg shrink-0 hover:bg-gold/20" :disabled="displayDate === 'Today'" @click="nextDay">
            <ChevronRight class="h-5 w-5" />
          </Button>
        </div>

        <div class="w-1/3 flex justify-end gap-3">
          <Button
            v-if="displayDate !== 'Today'"
            variant="ghost"
            class="text-primary hover:bg-gold/10 hover:text-gold transition-colors font-medium border border-transparent hover:border-gold/30"
            @click="goToToday"
          >
            Go to Today
          </Button>
          <Button variant="outline" hover="glow" class="gap-2 border-2 border-gold shadow-sm" @click="showAddFood = true">
            <Plus class="h-4 w-4" /> Log Food
          </Button>
        </div>
      </div>

      <!-- Main Split Content -->
      <div class="flex-1 flex gap-6 overflow-hidden">
        
        <!-- Left Column: Daily Summary -->
        <div class="w-72 shrink-0 flex flex-col gap-3">
          <div class="rounded-xl bg-orange-500/10 border border-orange-500/20 p-4 flex items-center gap-4">
            <div class="rounded-full bg-orange-500/20 p-2"><Flame class="h-5 w-5 text-orange-500" /></div>
            <div>
              <p class="text-xl font-bold text-foreground">{{ fmt(todayTotals.calories) }}</p>
              <p class="text-xs text-muted-foreground uppercase font-medium tracking-wider">Calories</p>
            </div>
          </div>
          <div class="rounded-xl bg-red-500/10 border border-red-500/20 p-4 flex items-center gap-4">
            <div class="rounded-full bg-red-500/20 p-2"><Beef class="h-5 w-5 text-red-500" /></div>
            <div>
              <p class="text-xl font-bold text-foreground">{{ fmt(todayTotals.protein) }}g</p>
              <p class="text-xs text-muted-foreground uppercase font-medium tracking-wider">Protein</p>
            </div>
          </div>
          <div class="rounded-xl bg-amber-500/10 border border-amber-500/20 p-4 flex items-center gap-4">
            <div class="rounded-full bg-amber-500/20 p-2"><Wheat class="h-5 w-5 text-amber-500" /></div>
            <div>
              <p class="text-xl font-bold text-foreground">{{ fmt(todayTotals.carbs) }}g</p>
              <p class="text-xs text-muted-foreground uppercase font-medium tracking-wider">Carbs</p>
            </div>
          </div>
          <div class="rounded-xl bg-yellow-500/10 border border-yellow-500/20 p-4 flex items-center gap-4">
            <div class="rounded-full bg-yellow-500/20 p-2"><Droplets class="h-5 w-5 text-yellow-500" /></div>
            <div>
              <p class="text-xl font-bold text-foreground">{{ fmt(todayTotals.fat) }}g</p>
              <p class="text-xs text-muted-foreground uppercase font-medium tracking-wider">Fat</p>
            </div>
          </div>
        </div>

        <!-- Right Column: Food Logs by Meal -->
        <div class="flex-1 overflow-y-auto scrollbar-hide pb-12 pr-2">
          <LoadingSpinner v-if="loading" class="py-8" />
          
          <div v-else-if="!todayLogs.length" class="py-12 text-center rounded-2xl border border-dashed border-border bg-card/10 h-full flex flex-col items-center justify-center">
            <Apple class="h-10 w-10 text-muted-foreground/30 mb-3" />
            <p class="text-lg font-medium text-foreground">Your diary is empty</p>
            <p class="text-sm text-muted-foreground mt-1">Tap "Log Food" to track your first meal</p>
          </div>

          <div v-else class="space-y-6">
            <!-- Iterate over meals dynamically -->
            <template v-for="meal in MEAL_TYPES" :key="meal.value">
              <div v-if="byMeal[meal.value] && byMeal[meal.value].length > 0" class="space-y-2">
                <!-- Group Header -->
                <button
                  class="w-full flex items-center justify-between border-b border-border/50 pb-2 px-1 cursor-pointer hover:opacity-80 transition-opacity focus:outline-none"
                  @click="toggleMeal(meal.value)"
                >
                  <div class="flex items-center gap-2">
                    <ChevronDown
                      class="h-5 w-5 text-muted-foreground transition-transform duration-200"
                      :class="{ '-rotate-90': !mealOpenState[meal.value] }"
                    />
                    <h3 class="font-semibold text-foreground flex items-center gap-2 text-lg">
                      <span>{{ meal.label.split(' ')[0] }}</span> 
                      <span>{{ meal.label.split(' ')[1] }}</span>
                    </h3>
                  </div>
                  <span class="text-sm font-medium text-muted-foreground">
                    {{ fmt(byMeal[meal.value].reduce((acc, log) => acc + (log.calories || 0), 0)) }} cal
                  </span>
                </button>

                <!-- Group Items -->
                <div v-show="mealOpenState[meal.value]" class="pt-2">
                  <Card variant="gold" class="bg-card/80 dark:bg-card/60 backdrop-blur-md overflow-hidden">
                  <CardContent class="p-0 divide-y divide-border">
                    <div
                      v-for="log in byMeal[meal.value]"
                      :key="log.id"
                      class="flex items-center gap-4 px-4 py-3 transition-colors duration-200 hover:bg-teal-500/5 group cursor-pointer"
                    >
                      <div class="rounded-full bg-emerald-500/10 p-2 shrink-0">
                        <Apple class="h-4 w-4 text-emerald-500" />
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="font-medium text-foreground text-sm truncate">{{ log.food_name }}</p>
                        <p class="text-xs text-muted-foreground">
                          {{ fmt(log.calories) }} cal · {{ log.servings || 1 }} serving(s)
                          <span v-if="log.notes" class="italic text-muted-foreground/70"> · {{ log.notes }}</span>
                        </p>
                      </div>
                      <div class="text-right shrink-0">
                        <p class="text-xs text-muted-foreground font-medium">
                          {{ fmt(log.protein) }}g P · {{ fmt(log.carbs) }}g C · {{ fmt(log.fat) }}g F
                        </p>
                      </div>
                      <button class="btn-delete rounded-md p-1.5 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity" @click.stop="promptDelete(log)">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                      </button>
                    </div>
                  </CardContent>
                </Card>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </main>

    <!-- Add Food Dialog -->
    <Dialog :open="showAddFood" @update:open="(val: boolean) => { if (!val) closeAddDialog() }">
      <DialogContent class="sm:max-w-xl dialog-solid border-2 border-gold shadow-xl max-h-[95vh] overflow-y-auto scrollbar-hide">
        <DialogHeader>
          <DialogTitle>Log Food</DialogTitle>
        </DialogHeader>
        <div class="space-y-4">
          <!-- Search -->
          <div v-if="!selectedFood">
            <label class="text-sm font-medium">Search food</label>
            <div class="relative mt-1">
              <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input v-model="searchQuery" placeholder="e.g., chicken, rice, banana..." class="pl-10" />
            </div>
            <LoadingSpinner v-if="searching" size="sm" class="mt-2" />
            <div v-else-if="searchResults.length" class="mt-2 max-h-48 space-y-1 overflow-y-auto scrollbar-hide rounded-lg border border-border">
              <button
                v-for="food in searchResults"
                :key="food.fdcId"
                class="w-full rounded-lg border border-transparent px-4 py-3 text-left transition-all duration-200 hover:border-teal-500/50 hover:bg-teal-500/10 cursor-pointer"
                @click="selectFood(food)"
              >
                <p class="font-medium text-foreground text-sm">{{ food.description }}</p>
                <p class="text-xs text-muted-foreground">{{ food.brandOwner }} · {{ food.nutrients?.calories || 0 }} cal</p>
              </button>
            </div>
          </div>

          <!-- Selected Food -->
          <div v-else class="space-y-4">
            <div class="flex items-center gap-3 rounded-xl bg-emerald-500/10 p-3">
              <Apple class="h-5 w-5 text-emerald-500" />
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-foreground text-sm truncate">{{ selectedFood.description }}</p>
                <p class="text-xs text-muted-foreground">{{ selectedFood.brandOwner }}</p>
              </div>
              <Button variant="outline" hover="lift" size="sm" @click="clearSelection">Change</Button>
            </div>

            <!-- Nutrition Breakdown -->
            <div class="rounded-xl border border-border p-4 space-y-3">
              <p class="text-sm font-semibold underline text-muted-foreground">
                Nutrition · {{ fmtDecimal(selectedFood.servingSize || 100) }}{{ selectedFood.servingUnit || 'g' }} per serving
              </p>
              <!-- Macros row -->
              <div class="grid grid-cols-4 gap-2 text-center">
                <div class="rounded-lg bg-orange-500/10 p-2">
                  <p class="text-sm font-bold text-foreground">{{ fmt((selectedFood.nutrients?.calories || 0) * servings) }}</p>
                  <p class="text-xs text-muted-foreground">cal</p>
                </div>
                <div class="rounded-lg bg-red-500/10 p-2">
                  <p class="text-sm font-bold text-foreground">{{ fmtDecimal((selectedFood.nutrients?.protein || 0) * servings) }}g</p>
                  <p class="text-xs text-muted-foreground">protein</p>
                </div>
                <div class="rounded-lg bg-amber-500/10 p-2">
                  <p class="text-sm font-bold text-foreground">{{ fmtDecimal((selectedFood.nutrients?.carbs || 0) * servings) }}g</p>
                  <p class="text-xs text-muted-foreground">carbs</p>
                </div>
                <div class="rounded-lg bg-yellow-500/10 p-2">
                  <p class="text-sm font-bold text-foreground">{{ fmtDecimal((selectedFood.nutrients?.fat || 0) * servings) }}g</p>
                  <p class="text-xs text-muted-foreground">fat</p>
                </div>
              </div>
              <!-- Other nutrients -->
              <div class="grid grid-cols-3 gap-2">
                <div class="flex justify-between rounded-lg border border-border p-2 text-xs">
                  <span class="text-muted-foreground">Fiber</span>
                  <span class="font-medium text-foreground">{{ fmtDecimal((selectedFood.nutrients?.fiber || 0) * servings) }}g</span>
                </div>
                <div class="flex justify-between rounded-lg border border-border p-2 text-xs">
                  <span class="text-muted-foreground">Sugar</span>
                  <span class="font-medium text-foreground">{{ fmtDecimal((selectedFood.nutrients?.sugar || 0) * servings) }}g</span>
                </div>
                <div class="flex justify-between rounded-lg border border-border p-2 text-xs">
                  <span class="text-muted-foreground">Sodium</span>
                  <span class="font-medium text-foreground">{{ fmtDecimal((selectedFood.nutrients?.sodium || 0) * servings) }}mg</span>
                </div>
              </div>
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
                  v-for="meal in MEAL_TYPES"
                  :key="meal.value"
                  :class="['rounded-lg border p-2 text-center text-xs transition-colors', mealType === meal.value ? 'border-gold bg-gold/10 text-foreground font-medium' : 'border-border hover:bg-accent']"
                  @click="mealType = meal.value"
                >{{ meal.label }}</button>
              </div>
            </div>

            <!-- Notes -->
            <div>
              <label class="text-sm font-medium">Notes (optional)</label>
              <Input v-model="notes" placeholder="e.g., with salad..." class="mt-1" />
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-3 pt-2">
            <Button variant="outline" hover="lift" class="flex-1" @click="closeAddDialog">Cancel</Button>
            <Button variant="outline" hover="glow" class="flex-1 border-2 border-gold" :disabled="!selectedFood || adding" @click="addFoodLog">
              {{ adding ? 'Adding...' : 'Log Food' }}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>

    <!-- Delete Confirmation -->
    <ConfirmDialog
      v-model:open="showDeleteDialog"
      title="Delete Food Log"
      :description="`Remove '${deletingLog?.food_name || ''}' from your diary? This can't be undone.`"
      confirm-label="Remove"
      variant="destructive"
      @confirm="confirmDelete"
    />
  </div>
</template>
