import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

/**
 * Button component with enhanced interactive feedback
 * 
 * Features:
 * - Smooth hover transitions with brightness/shadow changes
 * - Focus-visible ring for keyboard navigation (accessibility)
 * - Active state with subtle scale transform
 * - Disabled state with reduced opacity
 * 
 * @validates Requirements 1.2 - Interactive feedback for all components
 */
const buttonVariants = cva(
  // Base styles with enhanced transitions and interactive feedback
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium " +
  // Smooth transitions for all interactive states
  "transition-all duration-200 ease-out " +
  // Focus-visible ring for accessibility (keyboard navigation)
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background " +
  // Disabled state
  "disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed " +
  // Active state with subtle scale
  "active:scale-[0.98] active:opacity-90 " +
  // SVG icon handling
  "[&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          // Primary button with hover glow effect
          "bg-primary text-primary-foreground border border-primary/20 " +
          "hover:bg-primary/90 hover:shadow-[0_0_20px_rgba(99,102,241,0.3)] hover:border-primary/40",
        destructive:
          // Destructive with hover brightness
          "bg-destructive text-destructive-foreground shadow-sm border border-destructive/20 " +
          "hover:bg-destructive/90 hover:shadow-lg",
        outline:
          // Outline with hover background
          "border border-white/20 bg-transparent " +
          "hover:bg-white/5 hover:border-white/30 hover:text-white",
        secondary:
          // Secondary with subtle hover
          "border bg-secondary text-secondary-foreground border-white/10 " +
          "hover:bg-secondary/80 hover:border-white/20",
        ghost:
          // Ghost with hover background
          "border border-transparent " +
          "hover:bg-white/10 hover:text-white",
        link:
          // Link with underline on hover
          "text-primary underline-offset-4 " +
          "hover:underline hover:text-primary/80",
      },
      size: {
        default: "min-h-9 px-4 py-2",
        sm: "min-h-8 rounded-md px-3 text-xs",
        lg: "min-h-10 rounded-md px-8",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
