import type { ReactNode } from "react";

import { cn } from "../../utils/cn";

type BadgeTone = "neutral" | "valid" | "warning" | "blocked" | "info";

const tones: Record<BadgeTone, string> = {
  neutral: "border-slate-300 bg-slate-50 text-slate-700",
  valid: "border-green-300 bg-status-valid-bg text-status-valid",
  warning: "border-amber-300 bg-status-warning-bg text-status-warning",
  blocked: "border-red-300 bg-status-blocked-bg text-status-blocked",
  info: "border-blue-300 bg-evidence-bg text-blue-800",
};

export function Badge({
  children,
  className,
  tone = "neutral",
}: {
  children: ReactNode;
  className?: string;
  tone?: BadgeTone;
}) {
  return (
    <span
      className={cn(
        "inline-flex min-h-6 items-center gap-1 rounded-md border px-2 py-0.5 text-xs font-medium",
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
