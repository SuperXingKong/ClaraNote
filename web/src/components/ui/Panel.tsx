import type { ReactNode } from "react";

import { cn } from "../../utils/cn";

export function Panel({
  children,
  className,
  title,
  actions,
}: {
  children: ReactNode;
  className?: string;
  title?: string;
  actions?: ReactNode;
}) {
  return (
    <section
      className={cn(
        "min-h-0 rounded-panel border border-clinical-border bg-clinical-panel shadow-panel",
        className,
      )}
    >
      {(title || actions) && (
        <div className="flex min-h-12 items-center justify-between gap-3 border-b border-clinical-border px-4 py-3">
          {title ? <h2 className="text-sm font-semibold">{title}</h2> : <span />}
          {actions}
        </div>
      )}
      {children}
    </section>
  );
}
