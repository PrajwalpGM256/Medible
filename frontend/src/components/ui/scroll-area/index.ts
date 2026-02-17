import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as ScrollArea } from "./ScrollArea.vue"
export { default as ScrollBar } from "./ScrollBar.vue"

export const scrollAreaVariants = cva(
  "relative",
  {
    variants: {
      variant: {
        default: "",
        ghost: "[&_[data-slot=scroll-area-scrollbar]]:opacity-0 [&:hover_[data-slot=scroll-area-scrollbar]]:opacity-100",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

export const scrollBarVariants = cva(
  "flex touch-none p-px transition-colors select-none",
  {
    variants: {
      variant: {
        default: "bg-border/10",
        thin: "w-1.5",
        accent: "bg-primary/10",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

export type ScrollAreaVariants = VariantProps<typeof scrollAreaVariants>
