import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import ContentCard from '../components/ContentCard'
import type { Person } from '../types'

export default function PersonPage() {
  const { id } = useParams<{ id: string }>()
  const personId = Number(id)
  const { data: people } = useQuery({ queryKey: ['people'], queryFn: api.getPeople })
  const person = people?.find((p: Person) => p.id === personId)
  const { data, isLoading } = useQuery({ queryKey: ['personContent', personId], queryFn: () => api.getPersonContent(personId), enabled: !!personId })

  if (!person && !isLoading) return <p className="text-gray-500">Person not found.</p>

  return (
    <div className="space-y-6">
      {person && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center gap-4">
            {person.avatar_url && <img src={person.avatar_url} alt={person.name} className="w-16 h-16 rounded-full" />}
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{person.name}</h1>
              {person.bio && <p className="text-gray-600 mt-1">{person.bio}</p>}
              <p className="text-xs text-gray-400 mt-1">{person.source_count} sources</p>
            </div>
          </div>
        </div>
      )}
      {isLoading && <p className="text-gray-500 text-sm">Loading content...</p>}
      {data && (
        <div className="space-y-3">
          {data.items.map((item) => <ContentCard key={item.id} item={item} />)}
          {data.items.length === 0 && <p className="text-gray-500 text-sm">No content yet.</p>}
        </div>
      )}
    </div>
  )
}
