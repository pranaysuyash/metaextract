import * as React from "react";
import { cn } from "@/lib/utils";

interface TimelineProps extends React.HTMLAttributes<HTMLDivElement> {}

const Timeline = React.forwardRef<HTMLDivElement, TimelineProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("relative space-y-8", className)}
      {...props}
    />
  )
);
Timeline.displayName = "Timeline";

interface TimelineItemProps extends React.HTMLAttributes<HTMLDivElement> {}

const TimelineItem = React.forwardRef<HTMLDivElement, TimelineItemProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("relative flex gap-4", className)}
      {...props}
    />
  )
);
TimelineItem.displayName = "TimelineItem";

interface TimelineConnectorProps extends React.HTMLAttributes<HTMLDivElement> {}

const TimelineConnector = React.forwardRef<HTMLDivElement, TimelineConnectorProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "absolute left-4 top-8 bottom-0 w-0.5 bg-border",
        className
      )}
      {...props}
    />
  )
);
TimelineConnector.displayName = "TimelineConnector";

interface TimelineHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

const TimelineHeader = React.forwardRef<HTMLDivElement, TimelineHeaderProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex items-center gap-4 flex-1", className)}
      {...props}
    />
  )
);
TimelineHeader.displayName = "TimelineHeader";

interface TimelineIconProps extends React.HTMLAttributes<HTMLDivElement> {
  color?: 'emerald' | 'red' | 'yellow' | 'blue' | 'slate' | 'primary';
}

const TimelineIcon = React.forwardRef<HTMLDivElement, TimelineIconProps>(
  ({ className, color = 'primary', children, ...props }, ref) => {
    const colorClasses = {
      emerald: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
      red: 'bg-red-500/10 text-red-500 border-red-500/20',
      yellow: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
      blue: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
      slate: 'bg-slate-500/10 text-slate-500 border-slate-500/20',
      primary: 'bg-primary/10 text-primary border-primary/20',
    };

    return (
      <div
        ref={ref}
        className={cn(
          "flex h-8 w-8 items-center justify-center rounded-full border shadow-sm",
          colorClasses[color],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
TimelineIcon.displayName = "TimelineIcon";

interface TimelineTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {}

const TimelineTitle = React.forwardRef<HTMLHeadingElement, TimelineTitleProps>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      className={cn("font-semibold leading-none tracking-tight", className)}
      {...props}
    />
  )
);
TimelineTitle.displayName = "TimelineTitle";

interface TimelineTimeProps extends React.HTMLAttributes<HTMLParagraphElement> {}

const TimelineTime = React.forwardRef<HTMLParagraphElement, TimelineTimeProps>(
  ({ className, ...props }, ref) => (
    <p
      ref={ref}
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    />
  )
);
TimelineTime.displayName = "TimelineTime";

interface TimelineDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {}

const TimelineDescription = React.forwardRef<HTMLParagraphElement, TimelineDescriptionProps>(
  ({ className, ...props }, ref) => (
    <p
      ref={ref}
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    />
  )
);
TimelineDescription.displayName = "TimelineDescription";

interface TimelineContentProps extends React.HTMLAttributes<HTMLDivElement> {}

const TimelineContent = React.forwardRef<HTMLDivElement, TimelineContentProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("mt-2", className)}
      {...props}
    />
  )
);
TimelineContent.displayName = "TimelineContent";

export {
  Timeline,
  TimelineItem,
  TimelineConnector,
  TimelineHeader,
  TimelineIcon,
  TimelineTitle,
  TimelineTime,
  TimelineDescription,
  TimelineContent,
};