<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/services/api'
import type { AdminStats } from '@/types'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Users, Droplet, Apple, ShieldAlert, Activity, Search } from 'lucide-vue-next'
import { toast } from 'vue-sonner'

const stats = ref<AdminStats | null>(null)
const loading = ref(true)

async function fetchStats() {
  loading.value = true
  try {
    const response = await adminApi.getStats()
    stats.value = response.data.data
  } catch (err) {
    console.error('Failed to fetch admin stats', err)
    toast.error('Failed to load platform statistics')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Overview Cards -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card class="border-border/50 bg-background/50 backdrop-blur-xl shadow-xl overflow-hidden relative group">
        <div class="absolute inset-0 bg-gradient-to-br from-teal-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Total Users</CardTitle>
          <Users class="h-4 w-4 text-teal-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ loading ? '-' : stats?.users.total }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            {{ loading ? '...' : `${stats?.users.active} active accounts` }}
          </p>
        </CardContent>
      </Card>

      <Card class="border-border/50 bg-background/50 backdrop-blur-xl shadow-xl overflow-hidden relative group">
        <div class="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Total Medications</CardTitle>
          <Droplet class="h-4 w-4 text-cyan-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ loading ? '-' : stats?.content.total_medications }}</div>
          <p class="text-xs text-muted-foreground mt-1">Logged by all users</p>
        </CardContent>
      </Card>

      <Card class="border-border/50 bg-background/50 backdrop-blur-xl shadow-xl overflow-hidden relative group">
        <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Food Logs</CardTitle>
          <Apple class="h-4 w-4 text-emerald-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ loading ? '-' : stats?.content.total_food_logs }}</div>
          <p class="text-xs text-muted-foreground mt-1">Total meals recorded</p>
        </CardContent>
      </Card>

      <Card class="border-border/50 bg-background/50 backdrop-blur-xl shadow-xl overflow-hidden relative group">
        <div class="absolute inset-0 bg-gradient-to-br from-amber-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Interaction Checks</CardTitle>
          <ShieldAlert class="h-4 w-4 text-amber-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ loading ? '-' : stats?.content.total_interaction_checks }}</div>
          <p class="text-xs text-muted-foreground mt-1">Safety checks performed</p>
        </CardContent>
      </Card>
    </div>

    <!-- Data Tables -->
    <div class="grid gap-4 md:grid-cols-2">
      <!-- Top Drugs -->
      <Card class="border-border/50 bg-background/50 backdrop-blur-xl shadow-xl">
        <CardHeader>
          <div class="flex items-center gap-2">
            <Activity class="h-5 w-5 text-cyan-500" />
            <CardTitle>Top Medications</CardTitle>
          </div>
          <CardDescription>Most frequently added medications by users.</CardDescription>
        </CardHeader>
        <CardContent>
          <div v-if="loading" class="py-4 text-center text-sm text-muted-foreground">Loading...</div>
          <div v-else-if="stats?.top_drugs.length === 0" class="py-4 text-center text-sm text-muted-foreground">No medications logged yet.</div>
          <div v-else class="space-y-4">
            <div v-for="(drug, index) in stats?.top_drugs" :key="index" class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="flex h-6 w-6 items-center justify-center rounded-full bg-cyan-500/10 text-xs font-medium text-cyan-500">
                  {{ index + 1 }}
                </div>
                <span class="text-sm font-medium">{{ drug.drug_name }}</span>
              </div>
              <span class="text-sm text-muted-foreground">{{ drug.count }} users</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Top Foods -->
      <Card class="border-border/50 bg-background/50 backdrop-blur-xl shadow-xl">
        <CardHeader>
          <div class="flex items-center gap-2">
            <Search class="h-5 w-5 text-emerald-500" />
            <CardTitle>Top Food Searches</CardTitle>
          </div>
          <CardDescription>Most frequently searched food items.</CardDescription>
        </CardHeader>
        <CardContent>
           <div v-if="loading" class="py-4 text-center text-sm text-muted-foreground">Loading...</div>
          <div v-else-if="stats?.top_foods.length === 0" class="py-4 text-center text-sm text-muted-foreground">No foods searched yet.</div>
          <div v-else class="space-y-4">
            <div v-for="(food, index) in stats?.top_foods" :key="index" class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/10 text-xs font-medium text-emerald-500">
                  {{ index + 1 }}
                </div>
                <span class="text-sm font-medium capitalize">{{ food.food_name }}</span>
              </div>
              <span class="text-sm text-muted-foreground">{{ food.count }} searches</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
