import * as React from "react"

import { cn } from "@/lib/utils"

/**
 * Input component with enhanced interactive feedback
 * 
 * Features:
 * - Smooth hover transition with border highlight
 * - Focus state with primary border and subtle glow
 * - Disabled state with reduced opacity
 * 
 * @validates Requirements 1.2 - Interactive feedback for all components
 */
const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          // Base styles
          "flex h-9 w-full rounded-md border border-white/10 bg-white/5 px-3 py-1 text-base shadow-sm " +
          // Smooth transitions for interactive states
          "transition-all duration-200 ease-out " +
          // File input styles
          "file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground " +
          // Placeholder styles
          "placeholder:text-muted-foreground/60 " +
          // Hover state - subtle border highlight
          "hover:border-white/20 hover:bg-white/[0.07] " +
          // Focus state - primary border with glow
          "focus:outline-none focus:border-primary focus:bg-white/[0.07] focus:shadow-[0_0_0_3px_rgba(99,102,241,0.15)] " +
          // Focus-visible for keyboard navigation
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-1 focus-visible:ring-offset-background " +
          // Disabled state
          "disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:border-white/10 disabled:hover:bg-white/5 " +
          // Responsive text size
          "md:text-sm",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
