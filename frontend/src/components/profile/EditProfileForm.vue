<script setup lang="ts">
import { ref, computed } from 'vue'
import { User, Mail, Check, Loader2, Lock, Download, Trash2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { useAuthStore } from '@/stores/auth'
import ChangePasswordForm from '@/components/profile/ChangePasswordForm.vue'
import DataExportCard from '@/components/profile/DataExportCard.vue'
import DangerZone from '@/components/profile/DangerZone.vue'

const auth = useAuthStore()

const editing = ref(false)
const saving = ref(false)
const saved = ref(false)
const errorMsg = ref('')

const firstName = ref(auth.user?.first_name || '')
const lastName = ref(auth.user?.last_name || '')
const email = ref(auth.user?.email || '')

const hasChanges = computed(() =>
  firstName.value !== (auth.user?.first_name || '') ||
  lastName.value !== (auth.user?.last_name || '') ||
  email.value !== (auth.user?.email || '')
)

function startEdit() {
  firstName.value = auth.user?.first_name || ''
  lastName.value = auth.user?.last_name || ''
  email.value = auth.user?.email || ''
  editing.value = true
  errorMsg.value = ''
  saved.value = false
}

function cancelEdit() {
  editing.value = false
  errorMsg.value = ''
}

async function saveProfile() {
  if (!hasChanges.value) return
  saving.value = true
  errorMsg.value = ''

  const success = await auth.updateProfile({
    first_name: firstName.value.trim(),
    last_name: lastName.value.trim(),
    email: email.value.trim(),
  })

  saving.value = false
  if (success) {
    editing.value = false
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } else {
    errorMsg.value = auth.error || 'Update failed'
  }
}
</script>

<template>
  <Card variant="gold" class="bg-card/80 dark:bg-card/60 backdrop-blur-md">
    <CardHeader class="flex flex-row items-center justify-between pb-3">
      <CardTitle class="text-base">Profile Information</CardTitle>
      <button v-if="!editing" class="text-sm font-medium text-muted-foreground transition-all hover:text-teal-400 hover:drop-shadow-[0_0_6px_rgba(20,184,166,0.6)]" @click="startEdit">Edit</button>
    </CardHeader>
    <CardContent class="space-y-5">

      <!-- Read-only mode -->
      <template v-if="!editing">
        <div class="grid gap-3 sm:grid-cols-2">
          <div class="flex items-center gap-3 rounded-lg border border-border p-3">
            <User class="h-4 w-4 text-teal-500" />
            <div>
              <p class="text-xs text-muted-foreground">First Name</p>
              <p class="text-sm font-medium text-foreground">{{ auth.user?.first_name || 'Not set' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-3 rounded-lg border border-border p-3">
            <User class="h-4 w-4 text-teal-500" />
            <div>
              <p class="text-xs text-muted-foreground">Last Name</p>
              <p class="text-sm font-medium text-foreground">{{ auth.user?.last_name || 'Not set' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-3 rounded-lg border border-border p-3 sm:col-span-2">
            <Mail class="h-4 w-4 text-cyan-500" />
            <div>
              <p class="text-xs text-muted-foreground">Email</p>
              <p class="text-sm font-medium text-foreground">{{ auth.user?.email }}</p>
            </div>
          </div>
        </div>
        <div v-if="saved" class="flex items-center gap-2 text-sm text-emerald-600 dark:text-emerald-400">
          <Check class="h-4 w-4" /> Profile updated successfully
        </div>
      </template>

      <!-- Edit mode -->
      <template v-else>
        <div class="grid gap-3 sm:grid-cols-2">
          <div class="space-y-1">
            <label class="text-xs font-medium text-muted-foreground">First Name</label>
            <Input v-model="firstName" placeholder="First name" class="border-transparent border-b-border rounded-none focus:border-transparent focus:border-b-teal-500 focus-visible:ring-0 focus-visible:ring-offset-0" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-medium text-muted-foreground">Last Name</label>
            <Input v-model="lastName" placeholder="Last name" class="border-transparent border-b-border rounded-none focus:border-transparent focus:border-b-teal-500 focus-visible:ring-0 focus-visible:ring-offset-0" />
          </div>
          <div class="space-y-1 sm:col-span-2">
            <label class="text-xs font-medium text-muted-foreground">Email</label>
            <Input v-model="email" type="email" placeholder="your@email.com" class="border-transparent border-b-border rounded-none focus:border-transparent focus:border-b-teal-500 focus-visible:ring-0 focus-visible:ring-offset-0" />
          </div>
        </div>
        <p v-if="errorMsg" class="text-sm text-red-500">{{ errorMsg }}</p>
        <div class="flex gap-3 pt-1">
          <Button variant="outline" size="sm" hover="glow" @click="cancelEdit">Cancel</Button>
          <Button size="sm" hover="glow" :disabled="!hasChanges || saving" @click="saveProfile">
            <Loader2 v-if="saving" class="mr-2 h-4 w-4 animate-spin" />
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </Button>
        </div>
      </template>

      <!-- Profile Actions -->
      <div class="border-t border-border pt-4">
        <p class="text-xs font-medium text-muted-foreground mb-3">Profile Actions</p>
        <div class="flex flex-wrap gap-2">
          <ChangePasswordForm>
            <Button variant="outline" size="sm" hover="glow" class="gap-2">
              <Lock class="h-3.5 w-3.5" /> Change Password
            </Button>
          </ChangePasswordForm>

          <DataExportCard>
            <Button variant="outline" size="sm" hover="glow" class="gap-2">
              <Download class="h-3.5 w-3.5" /> Export Data
            </Button>
          </DataExportCard>

          <DangerZone>
            <Button variant="outline" size="sm" hover="glow" class="gap-2 text-red-500 border-red-500/30 hover:bg-red-500/10 hover:text-red-600">
              <Trash2 class="h-3.5 w-3.5" /> Delete Account
            </Button>
          </DangerZone>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

