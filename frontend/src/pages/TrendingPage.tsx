import { useDigestToday, useDigestHistory, useTags } from '../hooks/useApi'
import TagCloud from '../components/TagCloud'

export default function TrendingPage() {
  const { data: digest, isLoading: digestLoading } = useDigestToday()
  const { data: history } = useDigestHistory()
  const { data: tags = [] } = useTags()

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Today's Highlights</h2>
        {digestLoading && <p className="text-gray-500 text-sm">Loading...</p>}
        {digest ? (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="prose prose-sm max-w-none whitespace-pre-line">{digest.highlights}</div>
            {digest.hot_topics.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Hot Topics</h3>
                <div className="flex flex-wrap gap-2">
                  {digest.hot_topics.map((topic) => <span key={topic.tag} className="px-2 py-1 bg-orange-50 text-orange-700 text-xs rounded-full">{topic.tag} ({topic.count})</span>)}
                </div>
              </div>
            )}
          </div>
        ) : (!digestLoading && <p className="text-gray-500 text-sm">No digest available yet.</p>)}
      </section>
      {tags.length > 0 && (
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Tag Cloud</h2>
          <div className="bg-white rounded-lg border border-gray-200 p-6"><TagCloud tags={tags} /></div>
        </section>
      )}
      {history && history.length > 1 && (
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Past Digests</h2>
          <div className="space-y-3">
            {history.slice(1).map((d) => (
              <div key={d.id} className="bg-white rounded-lg border border-gray-200 p-4">
                <p className="text-sm font-medium text-gray-700 mb-2">{d.date}</p>
                <p className="text-sm text-gray-600 whitespace-pre-line">{d.highlights}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
