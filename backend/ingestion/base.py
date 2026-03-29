from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from backend.models import Source, SourceType

@dataclass
class RawContent:
    title: str
    url: str
    body: str | None
    published_at: datetime | None
    source_type: SourceType

class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self, source: Source) -> list[RawContent]:
        ...
