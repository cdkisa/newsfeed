import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import type { Person, SourceType } from '../types'

const SOURCE_TYPES: SourceType[] = ['blog', 'youtube', 'podcast', 'twitter', 'newsletter', 'github']

export default function AdminPage() {
  const [adminKey, setAdminKey] = useState('')
  const [tab, setTab] = useState<'people' | 'tags'>('people')

  if (!adminKey) {
    return (
      <div className="max-w-md mx-auto mt-12">
        <h2 className="text-xl font-bold mb-4">Admin Access</h2>
        <form onSubmit={(e) => { e.preventDefault(); const input = e.currentTarget.elements.namedItem('key') as HTMLInputElement; setAdminKey(input.value) }}>
          <input name="key" type="password" placeholder="Admin API Key" className="w-full px-3 py-2 border rounded mb-3" />
          <button type="submit" className="w-full px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Login</button>
        </form>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex gap-4 items-center">
        <button onClick={() => setTab('people')} className={`text-sm font-medium ${tab === 'people' ? 'text-blue-600 underline' : 'text-gray-600'}`}>People</button>
        <button onClick={() => setTab('tags')} className={`text-sm font-medium ${tab === 'tags' ? 'text-blue-600 underline' : 'text-gray-600'}`}>Tags</button>
        <div className="flex-1" />
        <TriggerIngestButton adminKey={adminKey} />
      </div>
      {tab === 'people' && <PeopleTab adminKey={adminKey} />}
      {tab === 'tags' && <TagsTab adminKey={adminKey} />}
    </div>
  )
}

function TriggerIngestButton({ adminKey }: { adminKey: string }) {
  const mutation = useMutation({ mutationFn: () => api.admin.triggerIngest(adminKey) })
  return <button onClick={() => mutation.mutate()} disabled={mutation.isPending} className="px-3 py-1.5 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50">{mutation.isPending ? 'Running...' : 'Run Ingestion Now'}</button>
}

function PeopleTab({ adminKey }: { adminKey: string }) {
  const queryClient = useQueryClient()
  const { data: people = [] } = useQuery({ queryKey: ['people'], queryFn: api.getPeople })
  const [name, setName] = useState('')
  const [sourceForm, setSourceForm] = useState<{ personId: number; type: SourceType; url: string } | null>(null)
  const [expandedPerson, setExpandedPerson] = useState<number | null>(null)
  const createPerson = useMutation({ mutationFn: (n: string) => api.admin.createPerson({ name: n }, adminKey), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['people'] }); setName('') } })
  const deletePerson = useMutation({ mutationFn: (id: number) => api.admin.deletePerson(id, adminKey), onSuccess: () => queryClient.invalidateQueries({ queryKey: ['people'] }) })
  const addSource = useMutation({ mutationFn: (data: { personId: number; type: string; url: string }) => api.admin.addSource(data.personId, { type: data.type, url: data.url }, adminKey), onSuccess: (_d, vars) => { queryClient.invalidateQueries({ queryKey: ['people'] }); queryClient.invalidateQueries({ queryKey: ['sources', vars.personId] }); setSourceForm(null) } })
  const deleteSource = useMutation({ mutationFn: (data: { sourceId: number; personId: number }) => api.admin.deleteSource(data.sourceId, adminKey), onSuccess: (_d, vars) => { queryClient.invalidateQueries({ queryKey: ['people'] }); queryClient.invalidateQueries({ queryKey: ['sources', vars.personId] }) } })

  return (
    <div className="space-y-4">
      <form onSubmit={(e) => { e.preventDefault(); if (name.trim()) createPerson.mutate(name.trim()) }} className="flex gap-2">
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Person name" className="flex-1 px-3 py-2 border rounded text-sm" />
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white text-sm rounded">Add Person</button>
      </form>
      {people.map((p: Person) => (
        <div key={p.id} className="bg-white border rounded-lg p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">{p.name}</p>
              <button onClick={() => setExpandedPerson(expandedPerson === p.id ? null : p.id)} className="text-xs text-gray-500 hover:text-gray-700">
                {p.source_count} sources {expandedPerson === p.id ? '▲' : '▼'}
              </button>
            </div>
            <div className="flex gap-2">
              <button onClick={() => setSourceForm({ personId: p.id, type: 'blog', url: '' })} className="text-xs text-blue-600 hover:underline">+ Source</button>
              <button onClick={() => deletePerson.mutate(p.id)} className="text-xs text-red-600 hover:underline">Delete</button>
            </div>
          </div>
          {expandedPerson === p.id && <SourceList personId={p.id} adminKey={adminKey} onDelete={(sourceId) => deleteSource.mutate({ sourceId, personId: p.id })} />}
          {sourceForm?.personId === p.id && (
            <form onSubmit={(e) => { e.preventDefault(); addSource.mutate(sourceForm) }} className="mt-3 flex gap-2">
              <select value={sourceForm.type} onChange={(e) => setSourceForm({ ...sourceForm, type: e.target.value as SourceType })} className="px-2 py-1 border rounded text-sm">
                {SOURCE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
              <input value={sourceForm.url} onChange={(e) => setSourceForm({ ...sourceForm, url: e.target.value })} placeholder="URL or handle" className="flex-1 px-2 py-1 border rounded text-sm" />
              <button type="submit" className="px-3 py-1 bg-blue-600 text-white text-sm rounded">Add</button>
              <button type="button" onClick={() => setSourceForm(null)} className="px-3 py-1 border text-sm rounded">Cancel</button>
            </form>
          )}
        </div>
      ))}
    </div>
  )
}

function SourceList({ personId, adminKey, onDelete }: { personId: number; adminKey: string; onDelete: (id: number) => void }) {
  const { data: sources = [], isLoading } = useQuery({ queryKey: ['sources', personId], queryFn: () => api.admin.getSources(personId, adminKey) })
  if (isLoading) return <p className="text-xs text-gray-400 mt-2">Loading...</p>
  if (sources.length === 0) return <p className="text-xs text-gray-400 mt-2">No sources yet.</p>
  return (
    <div className="mt-2 space-y-1">
      {sources.map((s) => (
        <div key={s.id} className="flex items-center gap-2 text-xs bg-gray-50 rounded px-2 py-1.5">
          <span className="font-medium text-gray-700 w-20">{s.type}</span>
          <span className="text-gray-500 flex-1 truncate">{s.url}</span>
          <span className={`px-1.5 py-0.5 rounded text-[10px] ${s.active ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-500'}`}>{s.active ? 'active' : 'inactive'}</span>
          <button onClick={() => onDelete(s.id)} className="text-red-500 hover:text-red-700">x</button>
        </div>
      ))}
    </div>
  )
}

function TagsTab({ adminKey }: { adminKey: string }) {
  const queryClient = useQueryClient()
  const { data: tags = [] } = useQuery({ queryKey: ['tags'], queryFn: api.getTags })
  const [name, setName] = useState('')
  const createTag = useMutation({ mutationFn: (n: string) => api.admin.createTag({ name: n }, adminKey), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['tags'] }); setName('') } })

  return (
    <div className="space-y-4">
      <form onSubmit={(e) => { e.preventDefault(); if (name.trim()) createTag.mutate(name.trim()) }} className="flex gap-2">
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Tag name" className="flex-1 px-3 py-2 border rounded text-sm" />
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white text-sm rounded">Add Tag</button>
      </form>
      <div className="flex flex-wrap gap-2">
        {tags.map((t) => <span key={t.slug} className="px-3 py-1.5 bg-white border rounded-full text-sm">{t.name} ({t.count})</span>)}
      </div>
    </div>
  )
}
