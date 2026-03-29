import { useState } from 'react'
import { Link } from 'react-router-dom'
import type { ContentItem } from '../types'
import SourceIcon from './SourceIcon'

export default function ContentCard({ item }: { item: ContentItem }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow flex flex-col h-full">
      <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
        {item.person_avatar_url && (
          <img src={item.person_avatar_url} alt={item.person_name} className="w-6 h-6 rounded-full flex-shrink-0" />
        )}
        <Link to={`/people/${item.person_id}`} className="font-medium text-gray-700 hover:text-blue-600">{item.person_name}</Link>
        <span>·</span>
        <SourceIcon type={item.source_type} />
      </div>
      <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-sm font-semibold text-gray-900 hover:text-blue-600 block mb-2 line-clamp-2">{item.title}</a>
      {item.summary && <p className={`text-xs text-gray-600 flex-1 ${expanded ? '' : 'line-clamp-3'}`}>{item.summary}</p>}
      {item.summary && item.summary.length > 150 && (
        <button onClick={() => setExpanded(!expanded)} className="text-xs text-blue-600 mt-1 hover:underline self-start">{expanded ? 'Show less' : 'Read more'}</button>
      )}
      <div className="mt-auto pt-3 flex items-center justify-between">
        {item.tags.length > 0 ? (
          <div className="flex gap-1 flex-wrap">
            {item.tags.slice(0, 2).map((tag) => (<span key={tag.id} className="px-2 py-0.5 bg-blue-50 text-blue-700 text-[10px] rounded-full">{tag.name}</span>))}
          </div>
        ) : <div />}
        {item.published_at && <span className="text-[10px] text-gray-400">{new Date(item.published_at).toLocaleDateString()}</span>}
      </div>
    </div>
  )
}
