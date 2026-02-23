<script setup lang="ts">
import { ref } from 'vue'
import { Lock, Check, Loader2, Eye, EyeOff } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const showCurrent = ref(false)
const showNew = ref(false)
const saving = ref(false)
const saved = ref(false)
const errorMsg = ref('')
const open = ref(false)

const PASSWORD_MIN_LENGTH = 8

function resetForm() {
  currentPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  errorMsg.value = ''
  saved.value = false
  showCurrent.value = false
  showNew.value = false
}

async function handleSubmit() {
  errorMsg.value = ''

  if (!currentPassword.value || !newPassword.value || !confirmPassword.value) {
    errorMsg.value = 'All fields are required'
    return
  }
  if (newPassword.value.length < PASSWORD_MIN_LENGTH) {
    errorMsg.value = `Password must be at least ${PASSWORD_MIN_LENGTH} characters`
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    errorMsg.value = 'New passwords do not match'
    return
  }
  if (currentPassword.value === newPassword.value) {
    errorMsg.value = 'New password must be different from current'
    return
  }

  saving.value = true
  const success = await auth.changePassword(currentPassword.value, newPassword.value)
  saving.value = false

  if (success) {
    saved.value = true
    resetForm()
    setTimeout(() => {
      saved.value = false
      open.value = false
    }, 1500)
  } else {
    errorMsg.value = auth.error || 'Password change failed'
  }
}
</script>

<template>
  <Dialog v-model:open="open" @update:open="(v) => { if (!v) resetForm() }">
    <DialogTrigger as-child>
      <slot />
    </DialogTrigger>
    <DialogContent class="sm:max-w-md border-2 border-gold shadow-xl">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <Lock class="h-4 w-4" /> Change Password
        </DialogTitle>
      </DialogHeader>
      <form class="space-y-4 py-2" @submit.prevent="handleSubmit">
        <div class="space-y-1">
          <label class="text-xs font-medium text-muted-foreground">Current Password</label>
          <div class="relative">
            <Input v-model="currentPassword" :type="showCurrent ? 'text' : 'password'" placeholder="Enter current password" class="pr-10" />
            <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" @click="showCurrent = !showCurrent">
              <Eye v-if="!showCurrent" class="h-4 w-4" /><EyeOff v-else class="h-4 w-4" />
            </button>
          </div>
        </div>
        <div class="space-y-1">
          <label class="text-xs font-medium text-muted-foreground">New Password</label>
          <div class="relative">
            <Input v-model="newPassword" :type="showNew ? 'text' : 'password'" placeholder="Enter new password" class="pr-10" />
            <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" @click="showNew = !showNew">
              <Eye v-if="!showNew" class="h-4 w-4" /><EyeOff v-else class="h-4 w-4" />
            </button>
          </div>
        </div>
        <div class="space-y-1">
          <label class="text-xs font-medium text-muted-foreground">Confirm New Password</label>
          <Input v-model="confirmPassword" type="password" placeholder="Confirm new password" />
        </div>

        <p v-if="errorMsg" class="text-sm text-red-500">{{ errorMsg }}</p>
        <div v-if="saved" class="flex items-center gap-2 text-sm text-emerald-600 dark:text-emerald-400">
          <Check class="h-4 w-4" /> Password changed successfully
        </div>

        <div class="flex gap-3 pt-1">
          <Button type="button" variant="outline" hover="glow" class="flex-1" @click="open = false">Cancel</Button>
          <Button type="submit" hover="glow" class="flex-1" :disabled="saving">
            <Loader2 v-if="saving" class="mr-2 h-4 w-4 animate-spin" />
            {{ saving ? 'Changing...' : 'Change Password' }}
          </Button>
        </div>
      </form>
    </DialogContent>
  </Dialog>
</template>
