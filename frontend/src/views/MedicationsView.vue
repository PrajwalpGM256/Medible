<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Pill, Plus, Search, Trash2, X } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent } from '@/components/ui/Card'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import AppNavbar from '@/components/common/AppNavbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { useMedicationsStore } from '@/stores/medications'
import { useDebouncedFn } from '@/composables/useDebounce'

const meds = useMedicationsStore()
const showAddDialog = ref(false)
const searchQuery = ref('')
const selectedDrug = ref('')
const dosage = ref('')

onMounted(() => { meds.fetchMedications() })

const debouncedSearch = useDebouncedFn((query: string) => { meds.searchDrugs(query) }, 300)

watch(searchQuery, (val) => { if (val.length >= 2) debouncedSearch(val); else meds.clearSearch() })

function selectDrug(drug: any) {
  selectedDrug.value = drug.brandName || drug.genericName
  searchQuery.value = ''
  meds.clearSearch()
}

async function handleAdd() {
  if (!selectedDrug.value) return
  const success = await meds.addMedication(selectedDrug.value, dosage.value)
  if (success) { showAddDialog.value = false; selectedDrug.value = ''; dosage.value = '' }
}

function closeDialog() {
  showAddDialog.value = false
  selectedDrug.value = ''
  dosage.value = ''
  searchQuery.value = ''
  meds.clearSearch()
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <AppNavbar />
    <main class="mx-auto max-w-4xl px-4 py-6 sm:px-6 sm:py-8">
      <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-bold text-foreground">My Medications</h1>
          <p class="text-muted-foreground">Manage your medication list</p>
        </div>
        <Dialog v-model:open="showAddDialog">
          <DialogTrigger as-child>
            <Button class="gap-2"><Plus class="h-4 w-4" />Add Medication</Button>
          </DialogTrigger>
          <DialogContent class="sm:max-w-md">
            <DialogHeader><DialogTitle>Add Medication</DialogTitle></DialogHeader>
            <div class="space-y-4 py-4">
              <div v-if="selectedDrug" class="flex items-center gap-2 rounded-lg bg-teal-500/10 p-3">
                <Pill class="h-5 w-5 text-teal-600" />
                <span class="flex-1 font-medium text-teal-700 dark:text-teal-300">{{ selectedDrug }}</span>
                <Button variant="ghost" size="icon" class="h-8 w-8" @click="selectedDrug = ''"><X class="h-4 w-4" /></Button>
              </div>
              <div v-else class="space-y-2">
                <div class="relative">
                  <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input v-model="searchQuery" placeholder="Search medications..." class="pl-10" />
                </div>
                <div v-if="meds.searchLoading" class="py-4"><LoadingSpinner size="sm" text="Searching..." /></div>
                <div v-else-if="meds.searchResults.length" class="max-h-48 space-y-1 overflow-y-auto">
                  <button v-for="drug in meds.searchResults" :key="drug.brandName" class="w-full rounded-lg p-3 text-left hover:bg-accent" @click="selectDrug(drug)">
                    <p class="font-medium text-foreground">{{ drug.brandName }}</p>
                    <p class="text-sm text-muted-foreground">{{ drug.genericName }}</p>
                  </button>
                </div>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium">Dosage (optional)</label>
                <Input v-model="dosage" placeholder="e.g., 10mg" />
              </div>
              <div class="flex gap-3 pt-2">
                <Button variant="outline" class="flex-1" @click="closeDialog">Cancel</Button>
                <Button class="flex-1" :disabled="!selectedDrug || meds.loading" @click="handleAdd">{{ meds.loading ? 'Adding...' : 'Add' }}</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
      <Card>
        <CardContent class="p-0">
          <LoadingSpinner v-if="meds.loading && !meds.medications.length" class="py-12" />
          <div v-else-if="!meds.medications.length" class="py-12 text-center">
            <Pill class="mx-auto h-12 w-12 text-muted-foreground/50" />
            <p class="mt-4 text-lg font-medium text-foreground">No medications yet</p>
            <p class="mt-1 text-muted-foreground">Add your first medication to get started</p>
          </div>
          <div v-else class="divide-y divide-border">
            <div v-for="med in meds.medications" :key="med.id" class="flex items-center gap-4 p-4">
              <div class="rounded-xl bg-teal-500/10 p-3"><Pill class="h-5 w-5 text-teal-600 dark:text-teal-400" /></div>
              <div class="flex-1">
                <p class="font-medium text-foreground">{{ med.drugName }}</p>
                <p class="text-sm text-muted-foreground">{{ med.dosage || 'No dosage' }} • {{ med.frequency || 'No schedule' }}</p>
              </div>
              <Button variant="ghost" size="icon" class="text-destructive hover:bg-destructive/10" @click="meds.removeMedication(med.id)"><Trash2 class="h-4 w-4" /></Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </main>
  </div>
</template>
