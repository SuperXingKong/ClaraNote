import * as Tooltip from "@radix-ui/react-tooltip";

import { cn } from "../../utils/cn";

export function EvidenceBadge({
  evidenceId,
  isSelected,
  onSelect,
}: {
  evidenceId: string;
  isSelected: boolean;
  onSelect: (id: string) => void;
}) {
  return (
    <Tooltip.Provider delayDuration={150}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <button
            className={cn(
              "inline-flex min-h-6 items-center rounded-md border px-2 text-xs font-semibold transition",
              isSelected
                ? "border-blue-700 bg-blue-700 text-white"
                : "border-evidence-border bg-evidence-bg text-blue-800 hover:bg-blue-100",
            )}
            onClick={() => onSelect(evidenceId)}
            type="button"
          >
            {evidenceId}
          </button>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content
            className="rounded-md bg-slate-950 px-2 py-1 text-xs text-white shadow-lg"
            sideOffset={6}
          >
            Highlight source span {evidenceId}
            <Tooltip.Arrow className="fill-slate-950" />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}
