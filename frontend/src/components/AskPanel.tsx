import { useState, useRef } from "react"
import { useAsk } from "@/hooks/useAsk"
import { useItems } from "@/hooks/useItems"
import { CitedAnswer } from "@/components/CitedAnswer"
import { SourceCard } from "@/components/SourceCard"

export function AskPanel() {
  const [question, setQuestion] = useState("")
  const [highlightedRef, setHighlightedRef] = useState<number | null>(null)
  const { mutate, data, isPending, error } = useAsk()
  const { data: items } = useItems()
  const sourceRefs = useRef<Record<number, HTMLDivElement | null>>({})

  const readyCount = items?.filter((i) => i.status === "ready").length ?? 0

  const handleAsk = () => {
    if (!question.trim() || isPending) return
    mutate(question.trim())
  }

  const handleCitationClick = (ref: number) => {
    setHighlightedRef(ref)
    sourceRefs.current[ref]?.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    })
    setTimeout(() => setHighlightedRef(null), 1500)
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <div className="flex items-center gap-2 text-sm text-neutral-600 mb-4">
        <span className="h-1.5 w-1.5 rounded-full bg-status-ready" />
        <span className="font-medium text-neutral-900">
          Knowledge base active
        </span>
        <span className="text-neutral-400">
          · {readyCount} item{readyCount === 1 ? "" : "s"} indexed
        </span>
      </div>

      <div className="rounded-lg border border-border-default bg-surface p-2 flex items-center gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          placeholder="Ask a question about your saved content..."
          className="flex-1 bg-transparent outline-none text-neutral-900 placeholder:text-neutral-400 px-2 py-2"
        />
        <button
          onClick={handleAsk}
          disabled={isPending || !question.trim()}
          className="bg-primary hover:bg-primary-hover disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium px-5 py-2 rounded-md transition-colors flex-shrink-0"
        >
          {isPending ? "Thinking..." : "Ask"}
        </button>
      </div>

      {error && (
        <p className="text-status-error text-sm mt-3">
          {(error as Error).message}
        </p>
      )}

      {data && (
        <div className="mt-6">
          <p className="text-neutral-400 text-xs font-medium uppercase tracking-wide mb-3">
            Synthesis from {data.sources.length} saved source
            {data.sources.length === 1 ? "" : "s"}
          </p>
          <div className="rounded-lg border border-border-hairline bg-surface p-4">
            <CitedAnswer
              answer={data.answer}
              sources={data.sources}
              onCitationClick={handleCitationClick}
            />
          </div>

          {data.sources.length > 0 && (
            <div className="mt-4">
              <p className="text-neutral-400 text-xs font-medium uppercase tracking-wide mb-2">
                Referenced documents · {data.sources.length} total
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {data.sources.map((s) => (
                  <SourceCard
                    key={s.ref}
                    source={s}
                    highlighted={highlightedRef === s.ref}
                    ref={(el) => {
                      sourceRefs.current[s.ref] = el
                    }}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
