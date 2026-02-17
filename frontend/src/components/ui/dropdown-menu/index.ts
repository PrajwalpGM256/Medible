import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as DropdownMenu } from "./DropdownMenu.vue"

export { default as DropdownMenuCheckboxItem } from "./DropdownMenuCheckboxItem.vue"
export { default as DropdownMenuContent } from "./DropdownMenuContent.vue"
export { default as DropdownMenuGroup } from "./DropdownMenuGroup.vue"
export { default as DropdownMenuItem } from "./DropdownMenuItem.vue"
export { default as DropdownMenuLabel } from "./DropdownMenuLabel.vue"
export { default as DropdownMenuRadioGroup } from "./DropdownMenuRadioGroup.vue"
export { default as DropdownMenuRadioItem } from "./DropdownMenuRadioItem.vue"
export { default as DropdownMenuSeparator } from "./DropdownMenuSeparator.vue"
export { default as DropdownMenuShortcut } from "./DropdownMenuShortcut.vue"
export { default as DropdownMenuSub } from "./DropdownMenuSub.vue"
export { default as DropdownMenuSubContent } from "./DropdownMenuSubContent.vue"
export { default as DropdownMenuSubTrigger } from "./DropdownMenuSubTrigger.vue"
export { default as DropdownMenuTrigger } from "./DropdownMenuTrigger.vue"
export { DropdownMenuPortal } from "reka-ui"

export const dropdownMenuItemVariants = cva(
  "focus:bg-accent focus:text-accent-foreground [&_svg:not([class*='text-'])]:text-muted-foreground relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 data-[inset]:pl-8 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 transition-colors",
  {
    variants: {
      variant: {
        default: "",
        destructive: "text-destructive focus:bg-destructive/10 dark:focus:bg-destructive/20 focus:text-destructive *:[svg]:!text-destructive",
        success: "text-emerald-600 focus:bg-emerald-50 dark:focus:bg-emerald-950/30 focus:text-emerald-700 dark:focus:text-emerald-400",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

export type DropdownMenuItemVariants = VariantProps<typeof dropdownMenuItemVariants>
