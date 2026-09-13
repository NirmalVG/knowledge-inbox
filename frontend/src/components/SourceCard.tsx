import { forwardRef } from "react"
import type { Source } from "@/lib/api"

export const SourceCard = forwardRef<
  HTMLDivElement,
  { source: Source; highlighted: boolean }
>(({ source, highlighted }, ref) => (
  <div
    ref={ref}
    className={`rounded-lg border p-3 transition-colors ${
      highlighted
        ? "border-primary bg-primary/5"
        : "border-border-hairline bg-surface"
    }`}
  >
    <div className="flex items-center justify-between mb-1">
      <span className="text-primary text-xs font-semibold">[{source.ref}]</span>
      <span className="text-neutral-400 text-xs">
        {Math.round(source.score * 100)}% match
      </span>
    </div>
    <p className="text-neutral-900 text-sm font-medium truncate">
      {source.item_title}
    </p>
    <p className="text-neutral-600 text-xs mt-1 line-clamp-2">
      {source.snippet}
    </p>
  </div>
))
SourceCard.displayName = "SourceCard"
