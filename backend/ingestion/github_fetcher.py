import logging
from datetime import datetime, timezone
import httpx
from backend.config import settings
from backend.ingestion.base import BaseFetcher, RawContent
from backend.models import Source, SourceType

logger = logging.getLogger(__name__)
EVENT_TYPES_OF_INTEREST = {"CreateEvent", "PushEvent", "ReleaseEvent", "PublicEvent"}

class GitHubFetcher(BaseFetcher):
    async def fetch(self, source: Source) -> list[RawContent]:
        username = source.url
        headers = {"Accept": "application/vnd.github.v3+json"}
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"https://api.github.com/users/{username}/events/public", headers=headers, timeout=30)
                events = resp.json()
        except Exception:
            logger.exception("Failed to fetch GitHub events for: %s", username)
            return []

        results: list[RawContent] = []
        for event in events:
            if event["type"] not in EVENT_TYPES_OF_INTEREST:
                continue
            created_at = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
            if source.last_fetched_at:
                cutoff = source.last_fetched_at
                if cutoff.tzinfo is None:
                    cutoff = cutoff.replace(tzinfo=timezone.utc)
                if created_at <= cutoff:
                    continue
            repo_name = event["repo"]["name"]
            event_type = event["type"]
            title = f"[{event_type}] {repo_name}"
            body = _describe_event(event)
            results.append(RawContent(title=title, url=f"https://github.com/{repo_name}", body=body, published_at=created_at, source_type=SourceType.github))
        return results

def _describe_event(event: dict) -> str:
    event_type = event["type"]
    payload = event.get("payload", {})
    repo = event["repo"]["name"]
    if event_type == "CreateEvent":
        ref_type = payload.get("ref_type", "")
        desc = payload.get("description", "") or ""
        return f"Created {ref_type} {repo}. {desc}".strip()
    elif event_type == "PushEvent":
        commits = payload.get("commits", [])
        messages = [c.get("message", "") for c in commits[:5]]
        return f"Pushed to {repo}: " + "; ".join(messages)
    elif event_type == "ReleaseEvent":
        release = payload.get("release", {})
        tag = release.get("tag_name", "")
        name = release.get("name", "")
        return f"Released {tag} ({name}) in {repo}"
    else:
        return f"{event_type} on {repo}"
