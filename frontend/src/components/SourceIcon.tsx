import type { SourceType } from '../types'

const ICONS: Record<SourceType, string> = { blog: '📝', youtube: '▶️', podcast: '🎙️', twitter: '🐦', newsletter: '📬', github: '🐙' }
const LABELS: Record<SourceType, string> = { blog: 'Blog', youtube: 'YouTube', podcast: 'Podcast', twitter: 'Twitter', newsletter: 'Newsletter', github: 'GitHub' }

export default function SourceIcon({ type }: { type: SourceType }) {
  return <span title={LABELS[type]} className="text-sm">{ICONS[type]} {LABELS[type]}</span>
}
