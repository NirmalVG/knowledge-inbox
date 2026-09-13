import { useState } from "react"
import { useIngestItem } from "@/hooks/useItems"
import type { ItemType } from "@/lib/api"

export function IngestPanel() {
  const [type, setType] = useState<ItemType>("url")
  const [content, setContent] = useState("")
  const { mutate, isPending, error } = useIngestItem()

  const handleSave = () => {
    if (!content.trim()) return
    mutate(
      { type, content: content.trim() },
      { onSuccess: () => setContent("") },
    )
  }

  return (
    <div className="mb-2">
      <div className="rounded-lg border border-border-default bg-surface p-2 flex items-center gap-2">
        <div className="flex bg-surface-substrate-alt rounded-md p-0.5 flex-shrink-0">
          {(["url", "note"] as ItemType[]).map((t) => (
            <button
              key={t}
              onClick={() => setType(t)}
              className={`px-3 py-1.5 rounded text-sm font-medium capitalize transition-colors ${
                type === t
                  ? "bg-white text-neutral-900 shadow-sm"
                  : "text-neutral-600"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
        <input
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSave()}
          placeholder={
            type === "url" ? "Paste a link..." : "Type a quick note..."
          }
          className="flex-1 bg-transparent outline-none text-neutral-900 placeholder:text-neutral-400 px-2"
        />
        <button
          onClick={handleSave}
          disabled={isPending || !content.trim()}
          className="bg-primary hover:bg-primary-hover disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium px-5 py-2 rounded-md transition-colors"
        >
          {isPending ? "Saving..." : "Save"}
        </button>
      </div>
      {error && (
        <p className="text-status-error text-xs mt-1.5 px-1">
          {(error as Error).message}
        </p>
      )}
    </div>
  )
}
