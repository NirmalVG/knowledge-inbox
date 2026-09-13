import type { Source } from "@/lib/api"

const CITATION_RE = /\[(\d+)\]/g

export function CitedAnswer({
  answer,
  sources,
  onCitationClick,
}: {
  answer: string
  sources: Source[]
  onCitationClick: (ref: number) => void
}) {
  const parts: React.ReactNode[] = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = CITATION_RE.exec(answer)) !== null) {
    const ref = parseInt(match[1], 10)
    const hasSource = sources.some((s) => s.ref === ref)

    parts.push(answer.slice(lastIndex, match.index))

    if (hasSource) {
      parts.push(
        <button
          key={match.index}
          onClick={() => onCitationClick(ref)}
          className="inline-flex items-center justify-center align-super text-[11px] font-medium bg-primary/10 text-primary rounded px-1 mx-0.5 hover:bg-primary/20 transition-colors"
        >
          {ref}
        </button>,
      )
    } else {
      // Defensive: a citation number the model emitted that doesn't match any
      // returned source. Shouldn't happen given how sources are built server-side
      // (Step 8a), but rendering it honestly rather than crashing or hiding it
      // is the right fallback if it ever does.
      parts.push(match[0])
    }
    lastIndex = match.index + match[0].length
  }
  parts.push(answer.slice(lastIndex))

  return <p className="text-neutral-900 leading-relaxed">{parts}</p>
}
