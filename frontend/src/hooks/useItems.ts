import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { fetchItems, ingestItem, deleteItem, type Item, type ItemType } from "@/lib/api"

const ITEMS_QUERY_KEY = ["items"]

export function useItems() {
  return useQuery({
    queryKey: ITEMS_QUERY_KEY,
    queryFn: fetchItems,
    // Poll while anything is still processing -- this is how the UI reflects
    // processing -> ready/failed without the user manually refreshing.
    refetchInterval: (query) => {
      const items = query.state.data as Item[] | undefined
      const hasProcessing = items?.some((i) => i.status === "processing")
      return hasProcessing ? 2000 : false
    },
  })
}

export function useIngestItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ type, content }: { type: ItemType; content: string }) =>
      ingestItem(type, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ITEMS_QUERY_KEY })
    },
  })
}

export function useDeleteItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteItem(id),
    onSuccess: (_, deletedId) => {
      // Remove it from the current list immediately. Refetch afterwards so the
      // client still converges on the server state if another tab changed it.
      queryClient.setQueryData<Item[]>(ITEMS_QUERY_KEY, (items) =>
        items?.filter((item) => item.id !== deletedId),
      )
      queryClient.invalidateQueries({ queryKey: ITEMS_QUERY_KEY })
    },
  })
}
