from abc import ABC, abstractmethod
from typing import Optional
from movie import Movie

class IMDbAdapter(ABC):
    @abstractmethod
    def get_movie(self, movie_id: str) -> Optional[Movie]:
        pass

    @abstractmethod
    def search_movie(self, title: str) -> Optional[Movie]:
        pass
