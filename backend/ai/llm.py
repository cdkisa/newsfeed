import litellm
from backend.config import settings

async def complete(prompt: str, system: str = "") -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = await litellm.acompletion(
        model=settings.llm_provider,
        messages=messages,
        api_key=settings.llm_api_key,
    )
    return response.choices[0].message.content
