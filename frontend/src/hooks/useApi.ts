import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function useContent(params?: Record<string, string>) {
  return useQuery({ queryKey: ['content', params], queryFn: () => api.getContent(params) })
}
export function usePeople() {
  return useQuery({ queryKey: ['people'], queryFn: api.getPeople })
}
export function usePersonContent(id: number) {
  return useQuery({ queryKey: ['personContent', id], queryFn: () => api.getPersonContent(id) })
}
export function useTags() {
  return useQuery({ queryKey: ['tags'], queryFn: api.getTags })
}
export function useDigestToday() {
  return useQuery({ queryKey: ['digestToday'], queryFn: api.getDigestToday, retry: false })
}
export function useDigestHistory() {
  return useQuery({ queryKey: ['digestHistory'], queryFn: api.getDigestHistory })
}
