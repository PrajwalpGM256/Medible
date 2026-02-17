<script setup lang="ts">
import type { HTMLAttributes } from "vue"
import type { SkeletonVariants } from "."
import { cn } from "@/lib/utils"
import { skeletonVariants } from "."

const props = defineProps<{
  variant?: SkeletonVariants["variant"]
  class?: HTMLAttributes["class"]
}>()
</script>

<template>
  <div
    data-slot="skeleton"
    :class="cn(skeletonVariants({ variant: props.variant }), props.class)"
  />
</template>
