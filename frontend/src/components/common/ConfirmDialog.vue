<script setup lang="ts">
import { computed } from 'vue'
import { AlertTriangle } from 'lucide-vue-next'
import { Button } from '@/components/ui/Button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

interface Props {
  open: boolean
  title?: string
  description: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: 'destructive' | 'default'
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Are you sure?',
  confirmLabel: 'Confirm',
  cancelLabel: 'Cancel',
  variant: 'destructive',
})

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

const isOpen = computed({
  get: () => props.open,
  set: (value: boolean) => emit('update:open', value),
})

const borderClass = computed(() =>
  props.variant === 'destructive'
    ? 'border-2 border-destructive/50'
    : 'border-2 border-gold',
)

function handleCancel() {
  emit('cancel')
  isOpen.value = false
}

function handleConfirm() {
  emit('confirm')
  isOpen.value = false
}
</script>

<template>
  <Dialog v-model:open="isOpen">
    <DialogContent class="sm:max-w-sm shadow-xl dialog-solid" :class="borderClass">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <AlertTriangle
            v-if="variant === 'destructive'"
            class="h-5 w-5 text-destructive"
          />
          {{ title }}
        </DialogTitle>
        <DialogDescription>
          <slot name="description">{{ description }}</slot>
        </DialogDescription>
      </DialogHeader>
      <DialogFooter class="flex gap-3 pt-2 sm:justify-end">
        <Button variant="outline" hover="lift" @click="handleCancel">{{ cancelLabel }}</Button>
        <Button variant="outline" hover="glow" @click="handleConfirm">
          {{ confirmLabel }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
