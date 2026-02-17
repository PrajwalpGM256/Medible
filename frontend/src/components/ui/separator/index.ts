import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as Separator } from "./Separator.vue"

export const separatorVariants = cva(
  "shrink-0 bg-border",
  {
    variants: {
      variant: {
        default: "bg-border",
        dashed: "bg-transparent border-t border-dashed border-border",
        dotted: "bg-transparent border-t border-dotted border-border",
        gradient: "bg-gradient-to-r from-transparent via-border to-transparent",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

export type SeparatorVariants = VariantProps<typeof separatorVariants>
