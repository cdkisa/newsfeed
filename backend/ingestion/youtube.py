import logging
from datetime import datetime, timezone
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from backend.config import settings
from backend.ingestion.base import BaseFetcher, RawContent
from backend.models import Source, SourceType

logger = logging.getLogger(__name__)

class YouTubeFetcher(BaseFetcher):
    async def fetch(self, source: Source) -> list[RawContent]:
        try:
            service = build("youtube", "v3", developerKey=settings.youtube_api_key)
            request = service.search().list(channelId=source.url, part="snippet", order="date", maxResults=10, type="video")
            response = request.execute()
        except Exception:
            logger.exception("Failed to fetch YouTube channel: %s", source.url)
            return []

        results: list[RawContent] = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            published = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))
            if source.last_fetched_at:
                cutoff = source.last_fetched_at
                if cutoff.tzinfo is None:
                    cutoff = cutoff.replace(tzinfo=timezone.utc)
                if published <= cutoff:
                    continue
            transcript_text = ""
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join(entry["text"] for entry in transcript)
            except Exception:
                logger.debug("No transcript for video %s", video_id)
            body = transcript_text or snippet.get("description", "")
            results.append(RawContent(title=snippet["title"], url=f"https://www.youtube.com/watch?v={video_id}", body=body, published_at=published, source_type=SourceType.youtube))
        return results
