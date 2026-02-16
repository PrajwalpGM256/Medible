<script setup lang="ts">
import { cn } from '@/lib/utils'

interface Props {
  title: string
  subtitle?: string
  centered?: boolean
  class?: string
}

withDefaults(defineProps<Props>(), {
  centered: true
})
</script>

<template>
  <div :class="cn('mb-12 sm:mb-16 max-w-2xl relative', centered && 'mx-auto text-center', $props.class)">
    <h2 class="text-3xl font-bold tracking-tight text-foreground sm:text-4xl inline-block bg-background/40 backdrop-blur-[2px] rounded-xl px-4 py-1">
      {{ title }}
    </h2>
    <p v-if="subtitle" class="mt-4 text-lg text-muted-foreground bg-background/50 backdrop-blur-[1px] rounded-lg p-2">
      {{ subtitle }}
    </p>
  </div>
</template>
