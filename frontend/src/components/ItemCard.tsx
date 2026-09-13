import { useState } from "react"
import { useDeleteItem } from "@/hooks/useItems"
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

  const { mutate: deleteItem } = useDeleteItem()
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  const handleDelete = () => {
    setShowDeleteModal(true)
  }

  const confirmDelete = () => {
    deleteItem(item.id, { onSuccess: () => setShowDeleteModal(false) })
  }

  return (
    <>
      <div className="border-b border-border-hairline py-4 flex items-start gap-3 relative group">
      <span
        className={`mt-2 h-2 w-2 rounded-full shrink-0 ${STATUS_COLOR[item.status]}`}
      />
      <div className="flex-1 min-w-0 pr-8">
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
        ) : item.preview ? (
          <p className="text-neutral-600 text-sm mt-0.5 line-clamp-2">
            {item.preview}
          </p>
        ) : null}
      </div>

      <button
        onClick={handleDelete}
        className="absolute top-3 right-0 w-8 h-8 rounded-md flex items-center justify-center opacity-0 group-hover:opacity-100 hover:bg-surface-substrate-alt text-neutral-400 hover:text-neutral-900 transition-all"
        title="Delete item"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 6h18"></path>
          <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
          <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
        </svg>
      </button>
      </div>
      {showDeleteModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-neutral-900/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby={`delete-item-${item.id}`}
          onMouseDown={() => setShowDeleteModal(false)}
        >
          <div
            className="w-full max-w-sm rounded-lg bg-surface p-6 shadow-xl"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <h2 id={`delete-item-${item.id}`} className="text-lg font-semibold text-neutral-900">
              Delete this item?
            </h2>
            <p className="mt-2 text-sm text-neutral-600">
              This will permanently remove “{item.title || "Untitled"}” and its saved content.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                className="rounded-md px-3 py-2 text-sm font-medium text-neutral-600 hover:bg-surface-substrate-alt"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={confirmDelete}
                className="rounded-md bg-status-error px-3 py-2 text-sm font-medium text-white hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
