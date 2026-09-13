import type { Item } from "@/lib/api"

function getDomain(url: string | null): string | null {
  if (!url) return null
  try {
    return new URL(url).hostname.replace(/^www\./, "")
  } catch {
    return null
  }
}

function timeAgo(iso: string): string {
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000)
  if (mins < 1) return "just now"
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

const STATUS_COLOR: Record<Item["status"], string> = {
  ready: "bg-status-ready",
  processing: "bg-status-processing",
  failed: "bg-status-error",
}

export function ItemCard({ item }: { item: Item }) {
  const sourceLabel =
    item.type === "url" ? getDomain(item.source_url) : "Personal Note"

  return (
    <div className="border-b border-border-hairline py-4 flex items-start gap-3">
      <span
        className={`mt-2 h-2 w-2 rounded-full shrink-0 ${STATUS_COLOR[item.status]}`}
      />
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline justify-between gap-3">
          <h3 className="text-neutral-900 font-medium truncate">
            {item.title || "Untitled"}
          </h3>
          <span className="text-neutral-400 text-xs whitespace-nowrap shrink-0">
            {sourceLabel} · {timeAgo(item.created_at)}
          </span>
        </div>
        {item.status === "failed" ? (
          <p className="text-status-error text-sm mt-0.5">
            {item.error_reason ?? "Processing failed"}
          </p>
        ) : (
          <p className="text-neutral-600 text-sm mt-0.5 line-clamp-2">
            {typeof (item as { summary?: string | null }).summary ===
              "string" && (item as { summary?: string | null }).summary?.trim()
              ? (item as { summary?: string | null }).summary
              : "No content available"}
          </p>
        )}
      </div>
    </div>
  )
}
