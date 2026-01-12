<script setup lang="ts">
import { Loader2 } from 'lucide-vue-next'

defineProps<{
  size?: 'sm' | 'md' | 'lg'
  text?: string
}>()

const sizeClasses = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' }
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-2">
    <Loader2 :class="sizeClasses[size || 'md']" class="animate-spin text-primary" />
    <span v-if="text" class="text-sm text-muted-foreground">{{ text }}</span>
  </div>
</template>
