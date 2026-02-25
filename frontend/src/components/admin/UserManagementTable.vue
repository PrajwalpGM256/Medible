<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/services/api'
import type { User } from '@/types'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import EditUserDialog from './EditUserDialog.vue'
import { UserPlus, Pencil, ShieldAlert, ShieldCheck, CheckCircle2, Ban } from 'lucide-vue-next'
import { toast } from 'vue-sonner'

const users = ref<User[]>([])
const loading = ref(true)
const showEditDialog = ref(false)
const selectedUser = ref<User | null>(null)

async function fetchUsers() {
  loading.value = true
  try {
    const response = await adminApi.getUsers({ per_page: 50, include_deleted: true })
    users.value = response.data.data.users
  } catch (err) {
    console.error('Failed to fetch users', err)
    toast.error('Failed to load users')
  } finally {
    loading.value = false
  }
}

function handleEdit(user: User) {
  selectedUser.value = user
  showEditDialog.value = true
}

function handleAdd() {
  selectedUser.value = null
  showEditDialog.value = true
}

async function toggleActive(user: User) {
  try {
    const newStatus = !user.is_active
    await adminApi.updateUser(user.id, { is_active: newStatus })
    toast.success(`User ${newStatus ? 'activated' : 'deactivated'} successfully`)
    fetchUsers()
  } catch (err: any) {
    toast.error(err.response?.data?.error?.message || 'Failed to update user status')
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <Card class="border-border/50 bg-background/50 backdrop-blur-xl shadow-xl">
    <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-7">
      <div class="space-y-1">
        <CardTitle class="text-xl">User Management</CardTitle>
        <CardDescription>View and manage registered users on the platform.</CardDescription>
      </div>
      <Button @click="handleAdd" hover="glow" class="gap-2">
        <UserPlus class="h-4 w-4" /> Add User
      </Button>
    </CardHeader>
    <CardContent>
      <div v-if="loading" class="py-12 text-center text-muted-foreground">Loading users...</div>
      
      <div v-else class="rounded-xl border border-border/50 overflow-hidden relative">
        <div class="overflow-x-auto">
          <table class="w-full text-sm text-left">
            <thead class="bg-muted/50 text-muted-foreground uppercase sticky top-0 backdrop-blur-md">
              <tr>
                <th scope="col" class="px-6 py-4 font-medium">User</th>
                <th scope="col" class="px-6 py-4 font-medium">Role</th>
                <th scope="col" class="px-6 py-4 font-medium">Status</th>
                <th scope="col" class="px-6 py-4 font-medium">Joined</th>
                <th scope="col" class="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border/50">
              <tr v-for="user in users" :key="user.id" class="bg-background/20 hover:bg-muted/20 transition-colors">
                <td class="px-6 py-4">
                  <div class="font-medium text-foreground">{{ user.full_name || 'N/A' }}</div>
                  <div class="text-muted-foreground text-xs mt-0.5">{{ user.email }}</div>
                </td>
                <td class="px-6 py-4">
                  <Badge :variant="user.is_admin ? 'default' : 'secondary'" class="gap-1 shadow-sm">
                    <ShieldCheck v-if="user.is_admin" class="h-3 w-3" />
                    <ShieldAlert v-else class="h-3 w-3 text-muted-foreground" />
                    {{ user.is_admin ? 'Admin' : 'User' }}
                  </Badge>
                </td>
                <td class="px-6 py-4">
                  <Badge :variant="user.is_active ? 'outline' : 'destructive'" class="gap-1 border-opacity-50">
                    <CheckCircle2 v-if="user.is_active" class="h-3 w-3 text-emerald-500" />
                    <Ban v-else class="h-3 w-3" />
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </Badge>
                </td>
                <td class="px-6 py-4 text-muted-foreground whitespace-nowrap">
                  {{ new Date(user.created_at || '').toLocaleDateString() }}
                </td>
                <td class="px-6 py-4 text-right">
                  <div class="flex items-center justify-end gap-2">
                    <Button variant="ghost" size="icon" class="h-8 w-8 text-muted-foreground hover:text-foreground hover:bg-muted/50" @click="handleEdit(user)" title="Edit Role">
                      <Pencil class="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" :class="['h-8 w-8', user.is_active ? 'text-destructive hover:text-destructive hover:bg-destructive/10' : 'text-emerald-500 hover:text-emerald-600 hover:bg-emerald-500/10']" @click="toggleActive(user)" :title="user.is_active ? 'Deactivate User' : 'Activate User'">
                      <Ban v-if="user.is_active" class="h-4 w-4" />
                      <CheckCircle2 v-else class="h-4 w-4" />
                    </Button>
                  </div>
                </td>
              </tr>
              <tr v-if="users.length === 0">
                <td colspan="5" class="px-6 py-12 text-center text-muted-foreground">No users found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </CardContent>
  </Card>

  <EditUserDialog 
    v-model:open="showEditDialog" 
    :user="selectedUser" 
    @saved="fetchUsers" 
  />
</template>
