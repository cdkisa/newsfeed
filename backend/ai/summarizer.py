from backend.ai.llm import complete
from backend.models import ContentItem, SourceType

SHORT_FORM_TYPES = {SourceType.twitter, SourceType.github}
SHORT_BODY_THRESHOLD = 200

async def summarize_content(item: ContentItem) -> str:
    body = item.body or ""
    if item.source_type in SHORT_FORM_TYPES or len(body) < SHORT_BODY_THRESHOLD:
        return body
    prompt = (
        f"Summarize the following content in 2-3 concise sentences. "
        f"Focus on the key takeaways.\n\n"
        f"Title: {item.title}\n\n"
        f"Content:\n{body[:8000]}"
    )
    return await complete(
        prompt=prompt,
        system="You are a concise technical summarizer for software engineering content.",
    )
