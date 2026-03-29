import type { TagWithCount } from '../types'

export default function TagCloud({ tags }: { tags: TagWithCount[] }) {
  const maxCount = Math.max(...tags.map((t) => t.count), 1)
  return (
    <div className="flex flex-wrap gap-2">
      {tags.map((tag) => {
        const size = 0.75 + (tag.count / maxCount) * 0.75
        return <span key={tag.slug} className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full cursor-default" style={{ fontSize: `${size}rem` }}>{tag.name} ({tag.count})</span>
      })}
    </div>
  )
}
