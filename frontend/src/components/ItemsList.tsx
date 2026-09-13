import { useState } from "react"
import { useItems } from "@/hooks/useItems"
import { ItemCard } from "@/components/ItemCard"
import type { ItemType } from "@/lib/api"

type Filter = "all" | ItemType

export function ItemsList() {
  const { data: items, isLoading, isError, error } = useItems()
  const [filter, setFilter] = useState<Filter>("all")

  if (isLoading) {
    return (
      <div className="flex flex-col gap-3 py-6">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-14 rounded-md bg-surface-substrate-alt animate-pulse"
          />
        ))}
      </div>
    )
  }

  if (isError) {
    return (
      <p className="text-status-error text-sm py-6">
        {(error as Error).message}
      </p>
    )
  }

  const filtered = (items ?? []).filter(
    (i) => filter === "all" || i.type === filter,
  )
  const processingCount = (items ?? []).filter(
    (i) => i.status === "processing",
  ).length

  return (
    <div>
      <div className="flex items-center justify-between py-3">
        <p className="text-neutral-600 text-sm">
          {items?.length ?? 0} saved item{items?.length === 1 ? "" : "s"}
          {processingCount > 0 && (
            <span className="text-status-processing">
              {" "}
              · {processingCount} processing
            </span>
          )}
        </p>
        <div className="flex gap-1">
          {(["all", "note", "url"] as Filter[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`cursor-pointer text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${
                filter === f
                  ? "bg-primary text-white"
                  : "bg-surface-substrate-alt text-neutral-600 hover:bg-border-default"
              }`}
            >
              {f === "all" ? "All" : f === "note" ? "Notes" : "Links"}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <p className="text-neutral-400 text-sm py-10 text-center">
          Nothing saved yet — add your first note or link above.
        </p>
      ) : (
        <div>
          {filtered.map((item) => (
            <ItemCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  )
}
