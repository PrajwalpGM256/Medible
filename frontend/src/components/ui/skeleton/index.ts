import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as Skeleton } from "./Skeleton.vue"

export const skeletonVariants = cva(
  "rounded-md bg-muted",
  {
    variants: {
      variant: {
        default: "animate-pulse",
        shimmer: "relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_2s_infinite] before:bg-gradient-to-r before:from-transparent before:via-white/20 before:to-transparent",
        pulse: "animate-pulse",
        glow: "animate-pulse bg-primary/20",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

export type SkeletonVariants = VariantProps<typeof skeletonVariants>
