from typing import Optional
from imdbinfo import get_movie as get_imdb_movie_from_lib
from imdbinfo import search_title
from imdb_adapter import IMDbAdapter
from movie import Movie
from exceptions import MovieNotFound

class IMDbInfoAdapter(IMDbAdapter):
    def get_movie(self, movie_id: str) -> Movie:
        try:
            movie_from_lib = get_imdb_movie_from_lib(movie_id)
            if not movie_from_lib:
                raise MovieNotFound(f"Movie with id {movie_id} not found.")

            return self._create_movie_from_imdb_movie(movie_from_lib)
        except Exception as e:
            raise MovieNotFound(f"Could not get movie with id {movie_id}. Reason: {e}")

    def search_movie(self, title: str) -> Movie:
        try:
            search_results = search_title(title)
            if not search_results.titles:
                raise MovieNotFound(f"Movie with title '{title}' not found.")

            title_words = set(title.lower().split())
            best_match = None
            highest_similarity = 0.0

            for movie_result in search_results.titles:
                result_title_words = set(movie_result.title.lower().split())
                
                # Jaccard similarity
                intersection_len = len(title_words.intersection(result_title_words))
                union_len = len(title_words.union(result_title_words))
                similarity = intersection_len / union_len if union_len > 0 else 0

                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = movie_result

            if best_match and highest_similarity > 0.8: # Setting a threshold
                return self.get_movie(best_match.imdb_id)

            raise MovieNotFound(f"Could not find a good match for title '{title}'.")

        except Exception as e:
            raise MovieNotFound(f"Could not find movie with title '{title}'. Reason: {e}")

    def _get_director(self, movie_from_lib: any) -> Optional[str]:
        if hasattr(movie_from_lib, 'directors') and movie_from_lib.directors:
            return movie_from_lib.directors[0].name
        return None

    def _create_movie_from_imdb_movie(self, movie_from_lib: any) -> Movie:
        return Movie(
            title=movie_from_lib.title,
            imdb_id=movie_from_lib.imdb_id,
            is_series=movie_from_lib.is_series(),
            director=self._get_director(movie_from_lib),
            duration=movie_from_lib.duration,
            rating=movie_from_lib.rating,
            plot=movie_from_lib.plot,
            genres=movie_from_lib.genres,
        )
