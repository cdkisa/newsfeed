export type SourceType = 'blog' | 'youtube' | 'podcast' | 'twitter' | 'newsletter' | 'github'
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface Tag { id: number; name: string; slug: string }
export interface TagWithCount extends Tag { count: number }
export interface Person { id: number; name: string; avatar_url: string | null; bio: string | null; source_count: number; created_at: string }
export interface Source { id: number; person_id: number; type: SourceType; url: string; active: boolean; last_fetched_at: string | null; created_at: string }
export interface ContentItem { id: number; person_id: number; person_name: string; person_avatar_url: string | null; title: string; url: string; summary: string | null; source_type: SourceType; published_at: string | null; processing_status: ProcessingStatus; tags: Tag[]; created_at: string }
export interface ContentList { items: ContentItem[]; total: number; page: number; page_size: number }
export interface DailyDigest { id: number; date: string; highlights: string; hot_topics: { tag: string; count: number; trend: string }[]; created_at: string }
