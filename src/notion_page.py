from dataclasses import dataclass
from typing import Optional

@dataclass
class NotionPage:
    id: str
    title: Optional[str] = None
    imdb_url: Optional[str] = None
