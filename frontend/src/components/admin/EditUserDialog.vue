<script setup lang="ts">
import { ref, watch } from 'vue'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/label'
import { adminApi } from '@/services/api'
import type { User } from '@/types'
import { toast } from 'vue-sonner'

const props = defineProps<{
  open: boolean
  user: User | null
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'saved'): void
}>()

const loading = ref(false)
const formData = ref({
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  is_admin: false,
  is_active: true
})

watch(() => props.open, (isOpen) => {
  if (isOpen && props.user) {
    formData.value = {
      email: props.user.email,
      password: '',
      first_name: props.user.first_name || '',
      last_name: props.user.last_name || '',
      is_admin: !!props.user.is_admin,
      is_active: props.user.is_active !== false
    }
  } else if (isOpen) {
    formData.value = {
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      is_admin: false,
      is_active: true
    }
  }
})

async function save() {
  loading.value = true
  try {
    if (props.user) {
      // Edit mode (Backend only supports updating is_active and is_admin via PATCH)
      await adminApi.updateUser(props.user.id, {
        is_admin: formData.value.is_admin,
        is_active: formData.value.is_active
      })
      toast.success('User updated successfully')
    } else {
      // Add mode
      await adminApi.createUser({
        email: formData.value.email,
        password: formData.value.password,
        first_name: formData.value.first_name,
        last_name: formData.value.last_name,
        is_admin: formData.value.is_admin,
        is_active: formData.value.is_active
      })
      toast.success('User created successfully')
    }
    emit('saved')
    emit('update:open', false)
  } catch (err: any) {
    toast.error(err.response?.data?.error?.message || 'Failed to save user')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>{{ user ? 'Manage User Role' : 'Add New User' }}</DialogTitle>
        <DialogDescription>
          {{ user ? 'Change the user role and login status.' : 'Create a new user profile manually.' }}
        </DialogDescription>
      </DialogHeader>

      <div class="grid gap-4 py-4">
        <!-- Fields only needed for Add mode -->
        <template v-if="!user">
          <div class="space-y-2">
            <Label for="email">Email</Label>
            <Input id="email" v-model="formData.email" placeholder="user@example.com" />
          </div>
          
          <div class="space-y-2">
            <Label for="password">Password</Label>
            <Input id="password" type="password" v-model="formData.password" placeholder="••••••••" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="firstName">First Name</Label>
              <Input id="firstName" v-model="formData.first_name" />
            </div>
            <div class="space-y-2">
              <Label for="lastName">Last Name</Label>
              <Input id="lastName" v-model="formData.last_name" />
            </div>
          </div>
        </template>
        
        <!-- User info display for Edit mode -->
        <template v-else>
          <div class="mb-2 p-3 bg-muted/30 rounded-lg border border-border/50">
            <div class="text-sm font-medium">{{ user.full_name || 'No Name Provided' }}</div>
            <div class="text-xs text-muted-foreground">{{ user.email }}</div>
          </div>
        </template>

        <!-- Common toggle fields -->
        <div class="flex items-center gap-3 mt-2 p-3 border border-border/50 rounded-lg bg-background/50">
          <input type="checkbox" id="isAdmin" v-model="formData.is_admin" class="w-4 h-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500 bg-background accent-teal-500" />
          <Label for="isAdmin" class="cursor-pointer font-medium select-none">Administrator Privileges</Label>
        </div>

        <div class="flex items-center gap-3 p-3 border border-border/50 rounded-lg bg-background/50">
          <input type="checkbox" id="isActive" v-model="formData.is_active" class="w-4 h-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500 bg-background accent-teal-500" />
          <Label for="isActive" class="cursor-pointer font-medium select-none">Account Active</Label>
        </div>
      </div>

      <DialogFooter class="mt-4">
        <Button variant="outline" @click="emit('update:open', false)">Cancel</Button>
        <Button @click="save" hover="glow" :disabled="loading">{{ loading ? 'Saving...' : 'Save Changes' }}</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
