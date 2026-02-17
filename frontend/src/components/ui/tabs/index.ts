import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as Tabs } from "./Tabs.vue"
export { default as TabsContent } from "./TabsContent.vue"
export { default as TabsList } from "./TabsList.vue"
export { default as TabsTrigger } from "./TabsTrigger.vue"

export const tabsVariants = cva(
  "w-full",
  {
    variants: {
      variant: {
        default: "",
        outline: "border rounded-lg p-1",
        pills: "bg-muted rounded-full p-1",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

export const tabsListVariants = cva(
  "inline-flex items-center justify-center rounded-md bg-muted p-1 text-muted-foreground",
  {
    variants: {
      variant: {
        default: "bg-muted",
        outline: "bg-transparent border",
        pills: "bg-muted rounded-full",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

export const tabsTriggerVariants = cva(
  "inline-flex items-center justify-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium whitespace-nowrap transition-all focus-visible:ring-ring/50 focus-visible:ring-[3px] disabled:pointer-events-none disabled:opacity-50 [&_svg]:size-4",
  {
    variants: {
      variant: {
        default: "data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm",
        underline: "rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:text-foreground",
        pills: "rounded-full data-[state=active]:bg-primary data-[state=active]:text-primary-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

export type TabsVariants = VariantProps<typeof tabsVariants>
export type TabsTriggerVariants = VariantProps<typeof tabsTriggerVariants>
