import { useState } from "react"
import { IngestPanel } from "@/components/IngestPanel"
import { ItemsList } from "@/components/ItemsList"
import { AskPanel } from "@/components/AskPanel"
import { StatusBanner } from "@/components/StatusBanner"

type View = "inbox" | "ask"

function App() {
  const [view, setView] = useState<View>("inbox")

  return (
    <div className="min-h-screen bg-surface-substrate-alt">
      <header className="border-b border-border-hairline bg-surface px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-md bg-primary flex items-center justify-center text-white text-sm font-bold">
            K
          </div>
          <span className="font-medium text-neutral-900">Knowledge Inbox</span>
        </div>
        <nav className="flex gap-6 text-sm">
          {(["inbox", "ask"] as View[]).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`cursor-pointer pb-3 -mb-3 capitalize ${
                view === v
                  ? "text-neutral-900 font-medium border-b-2 border-primary"
                  : "text-neutral-600 hover:text-neutral-900"
              }`}
            >
              {v}
            </button>
          ))}
        </nav>
        <div className="h-8 w-8 rounded-full bg-primary" />
      </header>

      <main>
        {view === "inbox" ? (
          <div className="max-w-2xl mx-auto px-6 py-10">
            <h1 className="text-3xl font-medium text-neutral-900 text-center mb-1">
              Knowledge Inbox
            </h1>
            <p className="text-neutral-600 text-center mb-8">
              Save anything you read or write. Ask questions anytime.
            </p>
            <IngestPanel />
            <ItemsList />
            <StatusBanner />
          </div>
        ) : (
          <AskPanel />
        )}
      </main>
    </div>
  )
}

export default App
