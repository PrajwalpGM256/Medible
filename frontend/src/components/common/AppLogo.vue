<script setup lang="ts">
import { Pill } from 'lucide-vue-next'
import { APP_NAME } from '@/constants'

defineProps<{
  size?: 'sm' | 'md' | 'lg'
  showText?: boolean
}>()

const sizeClasses = { sm: 'w-5 h-5', md: 'w-6 h-6', lg: 'w-8 h-8' }
const textClasses = { sm: 'text-lg', md: 'text-xl', lg: 'text-2xl' }
const paddingClasses = { sm: 'p-1.5', md: 'p-2', lg: 'p-2.5' }
</script>

<template>
  <div class="flex items-center gap-2">
    <div class="rounded-xl bg-gradient-to-br from-teal-500 to-cyan-500" :class="paddingClasses[size || 'md']">
      <Pill :class="sizeClasses[size || 'md']" class="text-white" />
    </div>
    <span v-if="showText !== false" :class="textClasses[size || 'md']" class="font-bold tracking-tight text-foreground">{{ APP_NAME }}</span>
  </div>
</template>
