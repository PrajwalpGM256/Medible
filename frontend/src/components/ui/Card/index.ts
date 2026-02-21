import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as Card } from "./Card.vue"
export { default as CardAction } from "./CardAction.vue"
export { default as CardContent } from "./CardContent.vue"
export { default as CardDescription } from "./CardDescription.vue"
export { default as CardFooter } from "./CardFooter.vue"
export { default as CardHeader } from "./CardHeader.vue"
export { default as CardTitle } from "./CardTitle.vue"

export const cardVariants = cva(
  "bg-card text-card-foreground flex flex-col gap-6 rounded-xl shadow-sm transition-all duration-300",
  {
    variants: {
      variant: {
        default: "border-2 border-foreground/10 dark:border bg-card py-6",
        outline: "border-2 border-border bg-background py-6",
        secondary: "bg-secondary/50 border-2 border-secondary py-6",
        destructive: "border-2 border-destructive/50 bg-destructive/5 py-6",
        glass: "bg-card/90 backdrop-blur-md border-2 border-foreground/10 dark:border py-6",
        ghost: "border-none bg-transparent shadow-none p-0",
        gold: "border-[0.5px] border-gold bg-card py-6",
      },
      hover: {
        none: "",
        lift: "hover:-translate-y-1 hover:shadow-lg hover:border-primary/50",
        glow: "hover:shadow-[0_0_20px_rgba(20,184,166,0.15)] hover:border-primary/50",
      },
    },
    defaultVariants: {
      variant: "default",
      hover: "none",
    },
  },
)

export type CardVariants = VariantProps<typeof cardVariants>
