<script setup lang="ts">
import type { LabelProps } from "reka-ui"
import type { HTMLAttributes } from "vue"
import type { LabelVariants } from "."
import { reactiveOmit } from "@vueuse/core"
import { Label } from "reka-ui"
import { cn } from "@/lib/utils"
import { labelVariants } from "."

const props = defineProps<LabelProps & { 
  class?: HTMLAttributes["class"]
  variant?: LabelVariants["variant"]
  size?: LabelVariants["size"]
}>()

const delegatedProps = reactiveOmit(props, ["class", "variant", "size"])
</script>

<template>
  <Label
    data-slot="label"
    v-bind="delegatedProps"
    :class="cn(labelVariants({ variant, size }), props.class)"
  >
    <slot />
  </Label>
</template>
