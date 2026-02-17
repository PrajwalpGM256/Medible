<script setup lang="ts">
import type { DropdownMenuItemProps } from "reka-ui"
import type { HTMLAttributes } from "vue"
import type { DropdownMenuItemVariants } from "."
import { reactiveOmit } from "@vueuse/core"
import { DropdownMenuItem, useForwardProps } from "reka-ui"
import { cn } from "@/lib/utils"
import { dropdownMenuItemVariants } from "."

const props = withDefaults(defineProps<DropdownMenuItemProps & {
  class?: HTMLAttributes["class"]
  inset?: boolean
  variant?: DropdownMenuItemVariants["variant"]
}>(), {
  variant: "default",
})

const delegatedProps = reactiveOmit(props, ["inset", "variant", "class"])
const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <DropdownMenuItem
    data-slot="dropdown-menu-item"
    :data-inset="inset ? '' : undefined"
    v-bind="forwardedProps"
    :class="cn(dropdownMenuItemVariants({ variant: props.variant }), props.class)"
  >
    <slot />
  </DropdownMenuItem>
</template>
