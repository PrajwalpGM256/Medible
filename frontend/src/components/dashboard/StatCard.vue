<script setup lang="ts">
import { LucideIcon } from 'lucide-vue-next'
import { Skeleton } from '@/components/ui/skeleton'

defineProps<{
  label: string
  value?: string | number
  icon: LucideIcon
  iconClass?: string
  loading?: boolean
}>()
</script>

<template>
  <div class="stat place-items-center p-0">
    <template v-if="loading">
      <div class="flex flex-col items-center gap-2">
        <Skeleton class="h-8 w-16" />
        <Skeleton class="h-4 w-24" />
      </div>
    </template>
    <template v-else>
      <div class="stat-figure" :class="iconClass">
        <component :is="icon" class="h-8 w-8" />
      </div>
      <div class="stat-title">{{ label }}</div>
      <div class="stat-value">{{ value ?? 0 }}</div>
    </template>
  </div>
</template>
