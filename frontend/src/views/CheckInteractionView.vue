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
  foodQuery.value = food.description
  foodResults.value = []
}

async function checkInteractions() {
  if (!selectedFood.value && foodQuery.value.length >= 2) {
    selectedFood.value = foodQuery.value
  }
  if (!selectedFood.value || !meds.medications.length) return
  checking.value = true
  hasChecked.value = true
  results.value = []
  try {
    const medNames = meds.medications.map(m => m.drugName)
    console.log('[CheckInteraction] Sending checkMultiple with:', { food: selectedFood.value, medNames })
    
    const { data } = await interactionApi.checkMultiple(selectedFood.value, medNames)
    console.log('[CheckInteraction] Raw response:', data)
    
    // API returns: { data: { food_checked, medications_checked, total_warnings, warnings: { high: [], medium: [], low: [] } } }
    const payload = data?.data || data || {}
    const warnings = payload?.warnings || { high: [], medium: [], low: [] }
    
    // Flatten warnings into results array safely
    const flattened = [
      ...(warnings.high || []).map((w: any) => ({ ...w, severity: 'high' })),
      ...(warnings.medium || []).map((w: any) => ({ ...w, severity: 'moderate' })),
      ...(warnings.low || []).map((w: any) => ({ ...w, severity: 'low' }))
    ]
    console.log('[CheckInteraction] Flattened warnings length:', flattened.length)
    
    // Map backend response fields to frontend expected fields
    const formatted = flattened.map(w => ({
      interaction_id: w.interaction_id,
      drug_matched: w.drug,
      food_matched: w.food,
      drug_class: w.drug_class,
      severity: w.severity,
      effect: w.effect,
      recommendation: w.recommendation,
      evidence_level: w.evidence_level
    }))

    if (formatted.length > 0) {
      results.value = formatted
    }

    console.log('[CheckInteraction] Saving history...')
    await historyStore.saveCheck(
      selectedFood.value,
      medNames,
      results.value
    )
    console.log('[CheckInteraction] History saved.')
  } catch (err) { 
    console.error('[CheckInteraction] Check failed with error:', err) 
  }
  finally { checking.value = false }
}

function clearResults() {
  selectedFood.value = ''
  results.value = []
  hasChecked.value = false
}

function reset() { 
  foodQuery.value = ''
  clearResults()
}

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

    <main class="flex-1 flex overflow-hidden w-full max-w-[1600px] mx-auto">
      
      <!-- Left Column: History (30%) -->
      <div v-if="historyStore.history.length" class="hidden lg:flex w-[30%] min-w-[320px] max-w-[400px] border-r border-border/30 bg-card/20 flex-col h-full px-5 py-6">
        <div class="flex items-center justify-between mb-5 shrink-0">
          <h2 class="text-lg font-bold text-foreground">Recent Checks</h2>
          <Button variant="ghost" size="sm" class="h-8 px-2 text-xs text-muted-foreground hover:text-destructive transition-colors" @click="showClearDialog = true">Clear All</Button>
        </div>
        
        <div class="flex-1 overflow-y-auto scrollbar-hide space-y-3 pr-1 pb-4">
          <div
            v-for="entry in historyStore.history"
            :key="entry.id"
            :class="[
              'rounded-xl border bg-card/80 p-4 transition-all duration-200 hover:bg-teal-500/10 cursor-pointer shadow-sm hover:shadow active:scale-[0.98]',
              entry.had_interaction ? 'border-amber-500/30' : 'border-emerald-500/30'
            ]"
            @click="foodQuery = entry.food_name; selectedFood = entry.food_name; checkInteractions()"
          >
            <div class="flex items-center gap-2.5 mb-2">
              <AlertTriangle v-if="entry.had_interaction" class="h-5 w-5 text-amber-500 shrink-0 drop-shadow-sm" />
              <CheckCircle v-else class="h-5 w-5 text-emerald-500 shrink-0 drop-shadow-sm" />
              <p class="text-base font-semibold text-foreground truncate">{{ entry.food_name }}</p>
            </div>
            <p class="text-sm font-medium text-muted-foreground mb-2">
              <span v-if="entry.had_interaction" class="text-amber-600 dark:text-amber-400">{{ entry.interaction_count }} interaction(s)</span>
              <span v-else class="text-emerald-600 dark:text-emerald-500">No interactions</span>
            </p>
            <div class="flex items-center gap-1.5 text-xs text-muted-foreground/50 font-medium">
              <Clock class="h-3.5 w-3.5" />
              {{ formatDate(entry.created_at) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Check Area (70%) -->
      <div class="flex-1 flex flex-col overflow-hidden px-4 md:px-8 py-6">
        
        <!-- Header -->
        <div class="mb-8 shrink-0 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 class="text-3xl font-extrabold text-gradient-animate tracking-tight">Check Interactions</h1>
            <p class="text-base text-muted-foreground mt-1 text-balance">Check if foods are safe with your medications</p>
          </div>
          <div class="shrink-0 flex items-center gap-2">
            <Button v-if="historyStore.history.length" variant="outline" size="sm" class="lg:hidden" @click="showClearDialog = true">
              Clear History
            </Button>
            <span class="inline-flex items-center gap-2 rounded-full bg-cyan-500/10 border border-cyan-500/20 px-4 py-1.5 text-sm font-bold text-cyan-700 dark:text-cyan-400 shadow-inner">
              <Pill class="h-4 w-4" />
              {{ meds.medications.length }} Active Meds
            </span>
          </div>
        </div>

        <!-- No Medications Warning -->
        <Card v-if="!meds.medications.length" variant="gold" class="mb-6 shrink-0 bg-amber-500/5 backdrop-blur-md shadow-sm">
          <CardContent class="flex items-center gap-5 p-6">
            <div class="h-12 w-12 rounded-full bg-amber-500/20 flex items-center justify-center shrink-0">
               <AlertTriangle class="h-6 w-6 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <p class="text-lg font-bold text-amber-700 dark:text-amber-300">No Medications Added</p>
              <p class="text-sm font-medium text-amber-600 dark:text-amber-500 mt-0.5 max-w-lg">You need to add your medications to your profile before you can check for food interactions.</p>
            </div>
          </CardContent>
        </Card>

        <!-- Search Bar Top -->
        <div class="mb-8 shrink-0 relative z-50 bg-card/60 backdrop-blur-md rounded-2xl border border-border shadow-md p-4 transition-all duration-300 hover:shadow-lg hover:border-border/80">
          <div class="flex flex-col sm:flex-row gap-3">
            <div class="relative flex-1 group">
              <Search class="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-teal-500" />
              <Input 
                v-model="foodQuery" 
                placeholder="What are you eating? (e.g. Grapefruit, Spinach)" 
                class="pl-12 h-14 text-base sm:text-lg bg-background/50 border-border/50 rounded-xl font-medium focus-visible:ring-teal-500/40 transition-all duration-200"
                @click="clearResults"
                @update:modelValue="clearResults"
                @keydown.enter="checkInteractions"
              />
              <LoadingSpinner v-if="searchingFood" size="sm" class="absolute right-4 top-1/2 -translate-y-1/2 text-teal-500" />
              <button v-else-if="foodQuery" @click="reset" class="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground p-1 rounded-full transition-colors">
                ✕
              </button>
            </div>
            <Button 
              variant="outline" hover="glow" 
              class="h-14 px-8 border-2 border-gold text-base font-bold tracking-wide w-full sm:w-auto transition-transform active:scale-95" 
              :disabled="checking || (!selectedFood && foodQuery.length < 2)" 
              @click="checkInteractions"
            >
              {{ checking ? 'Analyzing...' : 'Analyze' }}
            </Button>
          </div>

          <!-- Dropdown Results -->
          <div v-if="foodResults.length && !selectedFood && foodQuery.length >= 2" class="absolute z-50 left-4 right-4 sm:right-[140px] top-[calc(100%+0.5rem)] max-h-[300px] overflow-y-auto rounded-xl border-2 border-border bg-card shadow-2xl scrollbar-hide">
            <button
              v-for="food in foodResults"
              :key="food.fdcId"
              class="w-full flex flex-col border-b border-border/40 px-5 py-3.5 text-left transition-all hover:bg-teal-500/10 hover:pl-6 cursor-pointer last:border-0"
              @click="selectFood(food)"
            >
              <span class="font-semibold text-foreground text-base">{{ food.description }}</span>
              <span v-if="food.category" class="text-xs font-medium text-muted-foreground mt-0.5 uppercase tracking-wider">{{ food.category }}</span>
            </button>
          </div>
        </div>

        <!-- Scrollable Results -->
        <div class="flex-1 overflow-y-auto scrollbar-hide pb-12 relative rounded-xl">
          
          <div v-if="checking" class="absolute inset-0 flex flex-col items-center justify-center bg-background/50 backdrop-blur-sm z-10 rounded-xl">
            <LoadingSpinner size="lg" text="Cross-referencing databases..." class="scale-125" />
          </div>
          
          <div v-else-if="hasChecked && !results.length" class="flex flex-col items-center justify-center h-full text-center min-h-[400px] animate-in fade-in zoom-in duration-500">
            <div class="relative mb-8">
              <div class="absolute inset-0 bg-emerald-500/20 blur-2xl rounded-full scale-150 motion-safe:animate-pulse"></div>
              <div class="relative h-28 w-28 rounded-full bg-emerald-500/10 border-2 border-emerald-500/30 flex items-center justify-center shadow-inner">
                <CheckCircle class="h-14 w-14 text-emerald-500 drop-shadow-md" />
              </div>
            </div>
            <h2 class="text-4xl font-extrabold tracking-tight bg-gradient-to-br from-emerald-500 to-teal-400 bg-clip-text text-transparent mb-4">All Clear!</h2>
            <p class="text-xl font-medium text-muted-foreground max-w-lg leading-relaxed">No known interactions found between <span class="text-foreground font-bold decoration-wavy underline decoration-emerald-500/30 underline-offset-4">{{ selectedFood }}</span> and your active medications.</p>
          </div>

          <div v-else-if="hasChecked && results.length" class="space-y-6 animate-in slide-in-from-bottom-8 fade-in duration-500">
            <div class="flex items-center gap-3 pb-3 border-b border-border/40 px-1">
               <div class="p-2 rounded-lg bg-amber-500/10 shrink-0">
                  <AlertTriangle class="h-6 w-6 text-amber-500" />
               </div>
               <h2 class="text-2xl font-bold tracking-tight text-foreground">
                 Interactions found for <span class="bg-amber-500/10 px-2 py-0.5 rounded-md text-amber-600 dark:text-amber-400">{{ selectedFood }}</span>
               </h2>
               <span class="ml-auto flex items-center justify-center h-8 w-8 rounded-full bg-destructive/10 text-destructive font-bold">{{ results.length }}</span>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 pb-4">
              <Card
                v-for="(result, index) in results"
                :key="`${result.drug_matched}-${result.food_matched}-${index}`"
                variant="gold"
                class="group flex flex-col bg-card/80 dark:bg-card/60 backdrop-blur-md shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden border-border/50"
              >
                <!-- Thicker vibrant top border based on severity -->
                <div :class="['h-2 w-full transition-colors duration-300 group-hover:brightness-110', result.severity === 'high' ? 'bg-red-500' : result.severity === 'moderate' || result.severity === 'medium' ? 'bg-amber-500' : 'bg-blue-500']"></div>
                
                <CardHeader class="pb-3 flex-1 px-5 pt-5">
                  <div class="flex items-start justify-between gap-3 mb-3">
                    <CardTitle class="text-xl font-extrabold leading-tight tracking-tight text-foreground">
                       {{ result.drug_matched }}
                       <span v-if="result.drug_class" class="block text-xs font-semibold text-muted-foreground/70 uppercase tracking-widest mt-1">{{ result.drug_class.replace(/_/g, ' ') }}</span>
                    </CardTitle>
                    <span :class="[
                      'shrink-0 rounded-full px-3 py-1 text-xs font-bold uppercase tracking-widest shadow-sm', 
                      result.severity === 'high' ? 'bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20' : 
                      result.severity === 'moderate' || result.severity === 'medium' ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20' : 
                      'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20'
                    ]">
                      {{ result.severity }}
                    </span>
                  </div>
                  <p class="text-sm font-medium text-foreground/80 leading-relaxed">{{ result.effect }}</p>
                </CardHeader>
                
                <CardContent class="bg-muted/30 pt-4 pb-5 px-5 border-t border-border/40 mt-auto">
                  <p class="text-[10px] font-bold text-muted-foreground/80 uppercase tracking-widest mb-2 flex items-center gap-1.5">
                    <CheckCircle class="h-3 w-3" /> Action Plan
                  </p>
                  <p class="text-sm font-semibold leading-relaxed text-foreground/90">{{ result.recommendation }}</p>
                </CardContent>
              </Card>
            </div>
          </div>

          <div v-else class="flex flex-col items-center justify-center h-full text-center opacity-40 min-h-[400px]">
             <div class="relative mb-6">
                <Search class="h-20 w-20 text-muted-foreground drop-shadow-sm transition-transform hover:scale-110 duration-500" />
                <div class="absolute -bottom-2 -right-2 bg-background rounded-full p-1 border-2 border-border">
                   <Apple class="h-6 w-6 text-foreground/50" />
                </div>
             </div>
            <h3 class="text-2xl font-bold text-foreground">Ready to analyze</h3>
            <p class="text-lg font-medium text-muted-foreground mt-2 max-w-sm">Type a food item in the search bar above to see how it interacts with your medications.</p>
          </div>

        </div>

      </div>
    </main>

    <!-- Mobile History Overlay / Bottom drawer could go here in future, 
         for now we hide left column on mobile and suggest "Clear History" button in header -->

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
