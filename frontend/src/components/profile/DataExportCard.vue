<script setup lang="ts">
import { ref } from 'vue'
import { Download, FileJson, Loader2, Check } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useAuthStore } from '@/stores/auth'
import { foodDiaryApi, userMedicationApi } from '@/services/api'

const auth = useAuthStore()

const exporting = ref<string | null>(null)
const exported = ref<string | null>(null)

function downloadJson(data: unknown, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

async function exportAllData() {
  exporting.value = 'all'
  try {
    const data = await auth.exportData()
    if (data) {
      downloadJson(data, `medible-export-${new Date().toISOString().slice(0, 10)}.json`)
      exported.value = 'all'
      setTimeout(() => { exported.value = null }, 3000)
    }
  } finally {
    exporting.value = null
  }
}

async function exportFoodDiary() {
  exporting.value = 'food'
  try {
    const resp = await foodDiaryApi.getRange(
      new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      new Date().toISOString().slice(0, 10)
    )
    downloadJson(resp.data.data, `medible-food-diary-${new Date().toISOString().slice(0, 10)}.json`)
    exported.value = 'food'
    setTimeout(() => { exported.value = null }, 3000)
  } finally {
    exporting.value = null
  }
}

async function exportMedications() {
  exporting.value = 'meds'
  try {
    const resp = await userMedicationApi.getAll()
    downloadJson(resp.data.data, `medible-medications-${new Date().toISOString().slice(0, 10)}.json`)
    exported.value = 'meds'
    setTimeout(() => { exported.value = null }, 3000)
  } finally {
    exporting.value = null
  }
}

const EXPORT_OPTIONS = [
  { key: 'all', label: 'All My Data', desc: 'Profile, medications, food logs, interactions', action: exportAllData },
  { key: 'food', label: 'Food Diary', desc: 'All food diary entries', action: exportFoodDiary },
  { key: 'meds', label: 'Medications', desc: 'Current medication list', action: exportMedications },
] as const
</script>

<template>
  <Dialog>
    <DialogTrigger as-child>
      <slot />
    </DialogTrigger>
    <DialogContent class="sm:max-w-md border-2 border-gold shadow-xl">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <Download class="h-4 w-4" /> Data & Privacy
        </DialogTitle>
      </DialogHeader>
      <div class="py-2">
        <p class="mb-3 text-xs text-muted-foreground">Download your data as JSON files</p>
        <div class="space-y-2">
          <div
            v-for="opt in EXPORT_OPTIONS"
            :key="opt.key"
            class="flex items-center justify-between rounded-lg border border-border p-3 transition-colors hover:bg-accent/50"
          >
            <div class="flex items-center gap-3">
              <FileJson class="h-5 w-5 text-blue-500" />
              <div>
                <p class="text-sm font-medium text-foreground">{{ opt.label }}</p>
                <p class="text-xs text-muted-foreground">{{ opt.desc }}</p>
              </div>
            </div>
            <Button variant="outline" size="sm" hover="glow" :disabled="exporting !== null" @click="opt.action">
              <Loader2 v-if="exporting === opt.key" class="mr-1 h-3 w-3 animate-spin" />
              <Check v-else-if="exported === opt.key" class="mr-1 h-3 w-3 text-emerald-500" />
              <Download v-else class="mr-1 h-3 w-3" />
              {{ exporting === opt.key ? 'Exporting...' : exported === opt.key ? 'Done!' : 'Export' }}
            </Button>
          </div>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
