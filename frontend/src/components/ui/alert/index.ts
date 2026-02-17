import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as Alert } from "./Alert.vue"
export { default as AlertDescription } from "./AlertDescription.vue"
export { default as AlertTitle } from "./AlertTitle.vue"

export const alertVariants = cva(
  "relative w-full rounded-lg border px-4 py-3 text-sm grid has-[>svg]:grid-cols-[calc(var(--spacing)*4)_1fr] grid-cols-[0_1fr] has-[>svg]:gap-x-3 gap-y-0.5 items-start [&>svg]:size-4 [&>svg]:translate-y-0.5 [&>svg]:text-current transition-all duration-200",
  {
    variants: {
      variant: {
        default: "bg-card text-card-foreground",
        destructive:
          "text-destructive bg-card border-destructive/50 dark:border-destructive/30 *:data-[slot=alert-description]:text-destructive/90",
        success:
          "text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/20 border-emerald-500/50 dark:border-emerald-500/30 *:data-[slot=alert-description]:text-emerald-600 dark:data-[slot=alert-description]:text-emerald-500/80",
        warning:
          "text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/20 border-amber-500/50 dark:border-amber-500/30 *:data-[slot=alert-description]:text-amber-600 dark:data-[slot=alert-description]:text-amber-500/80",
        info:
          "text-teal-700 dark:text-teal-400 bg-teal-50 dark:bg-teal-950/20 border-teal-500/50 dark:border-teal-500/30 *:data-[slot=alert-description]:text-teal-600 dark:data-[slot=alert-description]:text-teal-500/80",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

export type AlertVariants = VariantProps<typeof alertVariants>
