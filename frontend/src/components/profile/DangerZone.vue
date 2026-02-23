<script setup lang="ts">
import { ref } from 'vue'
import { AlertTriangle, Loader2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from '@/components/ui/dialog'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ROUTES } from '@/constants'

const auth = useAuthStore()
const router = useRouter()

const open = ref(false)
const password = ref('')
const confirmText = ref('')
const deleting = ref(false)
const errorMsg = ref('')

const CONFIRM_WORD = 'DELETE'

function resetForm() {
  password.value = ''
  confirmText.value = ''
  errorMsg.value = ''
}

async function handleDelete() {
  if (confirmText.value !== CONFIRM_WORD) {
    errorMsg.value = `Please type ${CONFIRM_WORD} to confirm`
    return
  }
  if (!password.value) {
    errorMsg.value = 'Password is required'
    return
  }

  deleting.value = true
  errorMsg.value = ''

  const success = await auth.deleteAccount(password.value)
  deleting.value = false

  if (success) {
    open.value = false
    router.push(ROUTES.LOGIN)
  } else {
    errorMsg.value = auth.error || 'Failed to delete account'
  }
}
</script>

<template>
  <Dialog v-model:open="open" @update:open="(v) => { if (!v) resetForm() }">
    <DialogTrigger as-child>
      <slot />
    </DialogTrigger>
    <DialogContent class="sm:max-w-md border-red-500/50">
      <DialogHeader>
        <DialogTitle class="text-red-600 dark:text-red-400 flex items-center gap-2">
          <AlertTriangle class="h-4 w-4" /> Delete Account
        </DialogTitle>
        <DialogDescription>
          This will permanently delete your account, medications, food diary, and all interaction history.
        </DialogDescription>
      </DialogHeader>
      <div class="space-y-4 py-2">
        <div class="rounded-lg border border-red-500/30 bg-red-500/5 p-3">
          <p class="text-sm text-red-600 dark:text-red-400">
            ⚠️ This action is <strong>irreversible</strong>. All your data will be permanently removed.
          </p>
        </div>
        <div class="space-y-1">
          <label class="text-xs font-medium text-muted-foreground">
            Type <strong class="text-red-500">{{ CONFIRM_WORD }}</strong> to confirm
          </label>
          <Input v-model="confirmText" placeholder="Type DELETE" class="border-red-500/30 focus:border-red-500" />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-medium text-muted-foreground">Enter your password</label>
          <Input v-model="password" type="password" placeholder="Your password" />
        </div>
        <p v-if="errorMsg" class="text-sm text-red-500">{{ errorMsg }}</p>
        <div class="flex gap-3">
          <Button variant="outline" hover="glow" class="flex-1" :disabled="deleting" @click="open = false">Cancel</Button>
          <Button
            variant="destructive"
            hover="glow"
            class="flex-1"
            :disabled="confirmText !== CONFIRM_WORD || !password || deleting"
            @click="handleDelete"
          >
            <Loader2 v-if="deleting" class="mr-2 h-4 w-4 animate-spin" />
            {{ deleting ? 'Deleting...' : 'Delete My Account' }}
          </Button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
