<script setup lang="ts">
import type { HTMLAttributes } from "vue"
import type { AvatarVariants } from "."
import { AvatarRoot } from "reka-ui"
import { cn } from "@/lib/utils"
import { avatarVariants } from "."

const props = defineProps<{
  variant?: AvatarVariants["variant"]
  size?: AvatarVariants["size"]
  class?: HTMLAttributes["class"]
}>()
</script>

<template>
  <AvatarRoot
    data-slot="avatar"
    :class="cn(avatarVariants({ variant: props.variant, size: props.size }), 'relative flex shrink-0 overflow-hidden', props.class)"
  >
    <slot />
  </AvatarRoot>
</template>
