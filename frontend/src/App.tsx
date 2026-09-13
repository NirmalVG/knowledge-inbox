import { Button } from "@/components/ui/button"

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-substrate-alt">
      <div className="bg-surface border border-border-hairline rounded-lg p-8 flex flex-col gap-4">
        <h1 className="text-neutral-900 font-sans text-2xl font-medium">
          Clarity Canvas check
        </h1>
        <p className="text-neutral-600">
          If this button is indigo, the theme wired correctly.
        </p>
        <Button className="bg-primary hover:bg-primary-hover">Save</Button>
      </div>
    </div>
  )
}

export default App
