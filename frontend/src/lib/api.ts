const API_BASE = "http://localhost:8000"

export type ItemStatus = "processing" | "ready" | "failed"
export type ItemType = "note" | "url"

export interface Item {
  id: string
  type: ItemType
  title: string | null
  source_url: string | null
  status: ItemStatus
  char_count: number
  created_at: string
  error_reason?: string | null
}

export interface Source {
  ref: number
  item_id: string
  item_title: string
  snippet: string
  score: number
}

export interface QueryResult {
  answer: string
  sources: Source[]
}

export class ApiError extends Error {
  code: string
  status: number
  constructor(code: string, message: string, status: number) {
    super(message)
    this.code = code
    this.status = status
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    const code = body?.error?.code ?? "UNKNOWN_ERROR"
    const message =
      body?.error?.message ?? `Request failed with status ${res.status}`
    throw new ApiError(code, message, res.status)
  }
  return res.json()
}

export async function ingestItem(
  type: ItemType,
  content: string,
): Promise<Item> {
  const res = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type, content }),
  })
  return handleResponse<Item>(res)
}

export async function fetchItems(): Promise<Item[]> {
  const res = await fetch(`${API_BASE}/items`)
  const data = await handleResponse<{ items: Item[] }>(res)
  return data.items
}

export async function askQuestion(
  question: string,
  topK = 4,
): Promise<QueryResult> {
  const res = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: topK }),
  })
  return handleResponse<QueryResult>(res)
}
