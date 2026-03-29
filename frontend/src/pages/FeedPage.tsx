import { useState } from 'react'
import { useContent, usePeople, useTags } from '../hooks/useApi'
import ContentCard from '../components/ContentCard'
import FilterBar from '../components/FilterBar'

export default function FeedPage() {
  const [filters, setFilters] = useState<Record<string, string>>({})
  const [page, setPage] = useState(1)
  const params = { ...filters, page: String(page) }
  const { data, isLoading } = useContent(params)
  const { data: people = [] } = usePeople()
  const { data: tags = [] } = useTags()

  return (
    <div className="space-y-4">
      <FilterBar people={people} tags={tags} filters={filters} onChange={(f) => { setFilters(f); setPage(1) }} />
      {isLoading && <p className="text-gray-500 text-sm">Loading...</p>}
      {data && (
        <>
          <p className="text-xs text-gray-500">{data.total} items</p>
          <div className="space-y-3">{data.items.map((item) => <ContentCard key={item.id} item={item} />)}</div>
          {data.total > data.page_size && (
            <div className="flex justify-center gap-2 pt-4">
              <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 border rounded text-sm disabled:opacity-50">Previous</button>
              <span className="px-3 py-1 text-sm text-gray-600">Page {data.page} of {Math.ceil(data.total / data.page_size)}</span>
              <button onClick={() => setPage((p) => p + 1)} disabled={page >= Math.ceil(data.total / data.page_size)} className="px-3 py-1 border rounded text-sm disabled:opacity-50">Next</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
