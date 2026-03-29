import type { Person, TagWithCount, SourceType } from '../types'

const SOURCE_TYPES: { value: SourceType; label: string }[] = [
  { value: 'blog', label: 'Blog' }, { value: 'youtube', label: 'YouTube' },
  { value: 'podcast', label: 'Podcast' }, { value: 'twitter', label: 'Twitter' },
  { value: 'newsletter', label: 'Newsletter' }, { value: 'github', label: 'GitHub' },
]

interface FilterBarProps {
  people: Person[]; tags: TagWithCount[]
  filters: { person_id?: string; source_type?: string; tag_slug?: string; search?: string }
  onChange: (filters: Record<string, string>) => void
}

export default function FilterBar({ people, tags, filters, onChange }: FilterBarProps) {
  const update = (key: string, value: string) => {
    const next: Record<string, string> = { ...filters, [key]: value }
    if (!value) delete next[key]
    onChange(next)
  }
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 flex flex-wrap gap-3 items-center sticky top-14 z-40">
      <input type="text" placeholder="Search..." value={filters.search || ''} onChange={(e) => update('search', e.target.value)} className="px-3 py-1.5 border border-gray-300 rounded text-sm flex-1 min-w-48" />
      <select value={filters.person_id || ''} onChange={(e) => update('person_id', e.target.value)} className="px-3 py-1.5 border border-gray-300 rounded text-sm">
        <option value="">All people</option>
        {people.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
      </select>
      <select value={filters.source_type || ''} onChange={(e) => update('source_type', e.target.value)} className="px-3 py-1.5 border border-gray-300 rounded text-sm">
        <option value="">All sources</option>
        {SOURCE_TYPES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
      </select>
      <select value={filters.tag_slug || ''} onChange={(e) => update('tag_slug', e.target.value)} className="px-3 py-1.5 border border-gray-300 rounded text-sm">
        <option value="">All tags</option>
        {tags.map((t) => <option key={t.slug} value={t.slug}>{t.name} ({t.count})</option>)}
      </select>
    </div>
  )
}
