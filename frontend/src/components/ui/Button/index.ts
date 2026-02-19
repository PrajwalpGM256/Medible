import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as Button } from "./Button.vue"

export const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground border-2 border-primary/20 dark:border-none",
        destructive:
          "bg-destructive text-white hover:bg-destructive/90",
        outline:
          "border-2 bg-background border-foreground/20 dark:border-border",
        secondary:
          "bg-secondary text-secondary-foreground",
        ghost:
          "bg-transparent text-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        "default": "h-9 px-4 py-2 has-[>svg]:px-3",
        "sm": "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5",
        "lg": "h-10 rounded-md px-6 has-[>svg]:px-4",
        "icon": "size-9",
        "icon-sm": "size-8",
        "icon-lg": "size-10",
      },
      hover: {
        none: "",
        active: "hover:-translate-y-1 hover:shadow-lg active:scale-95 transition-all duration-300",
        glow: "hover:shadow-[0_0_20px_rgba(20,184,166,0.4)] transition-all duration-300",
        lift: "hover:-translate-y-1 hover:shadow-md transition-all duration-300",
        expand: "hover:scale-105 active:scale-95 transition-all duration-300",
        brutal: "hover:shadow-[4px_4px_0px_rgba(0,0,0,1)] dark:hover:shadow-[4px_4px_0px_rgba(20,184,166,1)] hover:-translate-x-1 hover:-translate-y-1 active:translate-x-0 active:translate-y-0 active:shadow-none transition-all duration-200",
        pulse: "hover:animate-pulse transition-all duration-300",
      },
    },
    compoundVariants: [
      {
        variant: "default",
        hover: "active",
        class: "hover:bg-teal-400 dark:hover:bg-teal-700",
      },
      {
        variant: "default",
        hover: "glow",
        class: "hover:bg-teal-500/90 hover:shadow-teal-500/50 dark:hover:bg-teal-600",
      },
      {
        variant: "outline",
        hover: "active",
        class: "hover:bg-teal-50 dark:hover:bg-slate-800 hover:text-teal-700 dark:hover:text-teal-400 hover:border-teal-600 dark:hover:border-teal-400",
      },
      {
        variant: "outline",
        hover: "glow",
        class: "hover:border-teal-500 hover:shadow-teal-500/20 hover:text-teal-600",
      },
      {
        variant: "secondary",
        hover: "active",
        class: "hover:bg-secondary/80",
      },
      {
        variant: "ghost",
        hover: "active",
        class: "hover:bg-teal-200 dark:hover:bg-teal-900/40 hover:text-black dark:hover:text-teal-200 hover:border-teal-300 dark:hover:border-teal-800 border border-transparent",
      },
    ],
    defaultVariants: {
      variant: "default",
      size: "default",
      hover: "none",
    },
  },
)
export type ButtonVariants = VariantProps<typeof buttonVariants>
