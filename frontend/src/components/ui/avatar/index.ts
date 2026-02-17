import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as Avatar } from "./Avatar.vue"
export { default as AvatarFallback } from "./AvatarFallback.vue"
export { default as AvatarImage } from "./AvatarImage.vue"

export const avatarVariants = cva(
  "inline-flex shrink-0 items-center justify-center overflow-hidden bg-muted",
  {
    variants: {
      variant: {
        circle: "rounded-full",
        square: "rounded-md",
        soft: "rounded-2xl",
      },
      size: {
        sm: "h-8 w-8 text-xs",
        default: "h-10 w-10 text-sm",
        lg: "h-12 w-12 text-base",
        xl: "h-16 w-16 text-lg",
      },
    },
    defaultVariants: {
      variant: "circle",
      size: "default",
    },
  },
)

export type AvatarVariants = VariantProps<typeof avatarVariants>
