const BASE_URL = '/api'

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const { headers, ...rest } = init || {}
  const resp = await fetch(`${BASE_URL}${path}`, {
    ...rest,
    headers: { 'Content-Type': 'application/json', ...headers },
  })
  if (!resp.ok) throw new Error(`API error: ${resp.status} ${resp.statusText}`)
  if (resp.status === 204) return undefined as T
  return resp.json()
}

export const api = {
  getContent: (params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : ''
    return fetchJson<import('../types').ContentList>(`/content${qs}`)
  },
  getContentById: (id: number) => fetchJson<import('../types').ContentItem>(`/content/${id}`),
  getPeople: () => fetchJson<import('../types').Person[]>('/people'),
  getPersonContent: (id: number, params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : ''
    return fetchJson<import('../types').ContentList>(`/people/${id}/content${qs}`)
  },
  getTags: () => fetchJson<import('../types').TagWithCount[]>('/tags'),
  getTagContent: (slug: string, params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : ''
    return fetchJson<import('../types').ContentList>(`/tags/${slug}/content${qs}`)
  },
  getDigestToday: () => fetchJson<import('../types').DailyDigest>('/digest/today'),
  getDigestHistory: () => fetchJson<import('../types').DailyDigest[]>('/digest/history'),
  admin: {
    createPerson: (data: { name: string; avatar_url?: string; bio?: string }, key: string) =>
      fetchJson<import('../types').Person>('/admin/people', { method: 'POST', body: JSON.stringify(data), headers: { 'X-Admin-Key': key } }),
    updatePerson: (id: number, data: Record<string, string>, key: string) =>
      fetchJson<import('../types').Person>(`/admin/people/${id}`, { method: 'PUT', body: JSON.stringify(data), headers: { 'X-Admin-Key': key } }),
    deletePerson: (id: number, key: string) =>
      fetchJson<void>(`/admin/people/${id}`, { method: 'DELETE', headers: { 'X-Admin-Key': key } }),
    addSource: (personId: number, data: { type: string; url: string }, key: string) =>
      fetchJson<import('../types').Source>(`/admin/people/${personId}/sources`, { method: 'POST', body: JSON.stringify(data), headers: { 'X-Admin-Key': key } }),
    deleteSource: (id: number, key: string) =>
      fetchJson<void>(`/admin/sources/${id}`, { method: 'DELETE', headers: { 'X-Admin-Key': key } }),
    createTag: (data: { name: string }, key: string) =>
      fetchJson<import('../types').Tag>('/admin/tags', { method: 'POST', body: JSON.stringify(data), headers: { 'X-Admin-Key': key } }),
    triggerIngest: (key: string) =>
      fetchJson<{ status: string; message: string }>('/admin/ingest/trigger', { method: 'POST', headers: { 'X-Admin-Key': key } }),
  },
}
