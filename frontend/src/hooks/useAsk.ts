import { useMutation } from "@tanstack/react-query"
import { askQuestion } from "@/lib/api"

export function useAsk() {
  return useMutation({
    mutationFn: (question: string) => askQuestion(question),
  })
}
