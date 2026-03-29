import { useState } from 'react'
import { Link } from 'react-router-dom'
import type { ContentItem } from '../types'
import SourceIcon from './SourceIcon'

export default function ContentCard({ item }: { item: ContentItem }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-sm transition-shadow">
      <div className="flex items-start gap-3">
        {item.person_avatar_url && (
          <img src={item.person_avatar_url} alt={item.person_name} className="w-10 h-10 rounded-full flex-shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
            <Link to={`/people/${item.person_id}`} className="font-medium text-gray-700 hover:text-blue-600">{item.person_name}</Link>
            <span>·</span>
            <SourceIcon type={item.source_type} />
            {item.published_at && (<><span>·</span><span>{new Date(item.published_at).toLocaleDateString()}</span></>)}
          </div>
          <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-base font-semibold text-gray-900 hover:text-blue-600 block mb-1">{item.title}</a>
          {item.summary && <p className={`text-sm text-gray-600 ${expanded ? '' : 'line-clamp-2'}`}>{item.summary}</p>}
          {item.summary && item.summary.length > 150 && (
            <button onClick={() => setExpanded(!expanded)} className="text-xs text-blue-600 mt-1 hover:underline">{expanded ? 'Show less' : 'Read more'}</button>
          )}
          {item.tags.length > 0 && (
            <div className="flex gap-1.5 mt-2 flex-wrap">
              {item.tags.map((tag) => (<span key={tag.id} className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full">{tag.name}</span>))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
