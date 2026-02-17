<script setup lang="ts">
import type { HTMLAttributes } from "vue"
import type { CardVariants } from "."
import { cn } from "@/lib/utils"
import { cardVariants } from "."

const props = defineProps<{
  variant?: CardVariants["variant"]
  hover?: CardVariants["hover"]
  class?: HTMLAttributes["class"]
}>()
</script>

<template>
  <div
    data-slot="card"
    :class="cn(cardVariants({ variant: props.variant, hover: props.hover }), props.class)"
  >
    <slot />
  </div>
</template>
