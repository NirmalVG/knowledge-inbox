import { useItems } from "@/hooks/useItems"

export function StatusBanner() {
  const { data: items } = useItems()
  
  if (!items || items.length === 0) return null
  
  const readyCount = items.filter(i => i.status === "ready").length
  const processingCount = items.filter(i => i.status === "processing").length
  const totalCount = items.length
  
  const isProcessing = processingCount > 0
  
  return (
    <div className="mt-6 rounded-lg bg-surface-substrate-alt border border-border-hairline p-4 flex items-center gap-3">
      <div className="flex items-center gap-2">
        <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
        </svg>
        <div>
          <p className="text-sm font-medium text-neutral-900">Knowledge Synthesis</p>
          <p className="text-xs text-neutral-600">
            {isProcessing
              ? `Processing ${processingCount} of ${totalCount} items...`
              : `All ${readyCount} items are embedded and ready for semantic querying.`}
          </p>
        </div>
      </div>
    </div>
  )
}
