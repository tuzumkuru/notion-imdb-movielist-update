from typing import Optional
from imdbinfo import get_movie as get_imdb_movie_from_lib
from imdbinfo import search_title
from imdb_adapter import IMDbAdapter
from movie import Movie

class IMDbInfoAdapter(IMDbAdapter):
    def get_movie(self, movie_id: str) -> Optional[Movie]:
        try:
            movie_from_lib = get_imdb_movie_from_lib(movie_id)
            if not movie_from_lib:
                return None

            director = None
            if hasattr(movie_from_lib, 'directors') and movie_from_lib.directors:
                director = movie_from_lib.directors[0].name

            return Movie(
                title=movie_from_lib.title,
                imdb_id=movie_from_lib.imdb_id,
                is_series=movie_from_lib.is_series(),
                director=director,
                duration=movie_from_lib.duration,
                rating=movie_from_lib.rating,
                plot=movie_from_lib.plot,
                genres=movie_from_lib.genres,
            )
        except Exception:
            return None

    def search_movie(self, title: str) -> Optional[Movie]:
        try:
            search_results = search_title(title)
            if not search_results.titles:
                return None
            
            return self.get_movie(search_results.titles[0].imdb_id)
        except Exception:
            return None
