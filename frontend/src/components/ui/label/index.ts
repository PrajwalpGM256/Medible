import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as Label } from "./Label.vue"

export const labelVariants = cva(
  "flex items-center gap-2 text-sm leading-none font-medium select-none group-data-[disabled=true]:pointer-events-none group-data-[disabled=true]:opacity-50 peer-disabled:cursor-not-allowed peer-disabled:opacity-50 transition-colors",
  {
    variants: {
      variant: {
        default: "text-foreground",
        muted: "text-muted-foreground font-normal",
        error: "text-destructive",
        required: "after:content-['*'] after:ml-0.5 after:text-destructive",
      },
      size: {
        default: "text-sm",
        sm: "text-xs",
        lg: "text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
)

export type LabelVariants = VariantProps<typeof labelVariants>
