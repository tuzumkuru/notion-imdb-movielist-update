from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Movie:
    title: str
    imdb_id: str
    is_series: bool
    director: Optional[str] = None
    duration: Optional[int] = None
    rating: Optional[float] = None
    plot: Optional[str] = None
    genres: Optional[List[str]] = None
