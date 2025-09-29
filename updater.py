from notion_api import NotionAPI
from imdb_adapter import IMDbAdapter
from movie import Movie
from notion_page import NotionPage
from logger import get_logger
from exceptions import MovieNotFound
import re

logger = get_logger(__name__)

class Updater:
    def __init__(self, notion_api: NotionAPI, imdb_adapter: IMDbAdapter):
        self._notion_api = notion_api
        self._imdb_adapter = imdb_adapter

    def update_page(self, page: NotionPage):
        try:
            logger.info(f"Updating the movie: {page.title}")
            movie = self._get_movie_from_page(page)
            properties = self._create_notion_properties(movie)
            self._notion_api.update_page(page.id, properties)
            logger.info(f"Successfully updated {movie.title}")
        except MovieNotFound as e:
            logger.error(f"Failed to update {page.title}: {e}")

    def _get_movie_from_page(self, page: NotionPage) -> Movie:
        if page.imdb_url:
            movie_id = self._get_id_from_url(page.imdb_url)
            if movie_id:
                return self._imdb_adapter.get_movie(movie_id)
        
        if page.title:
            return self._imdb_adapter.search_movie(page.title)

        raise MovieNotFound("Page has no title or IMDb URL.")

    def _get_id_from_url(self, url: str) -> str | None:
        pattern = r"tt(\d+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def _create_notion_properties(self, movie: Movie) -> dict:
        properties = {
            "Title": {"title": [{"text": {"content": movie.title}}]},
            "IMDB": {"url": f"https://www.imdb.com/title/tt{movie.imdb_id}"},
        }
        if movie.director and not movie.is_series:
            properties["Director"] = {"select": {"name": movie.director}}
        if movie.duration:
            properties["Duration [min]"] = {"number": movie.duration}
        if movie.rating:
            properties["IMDB Rating"] = {"number": movie.rating}
        if movie.plot:
            properties["Description"] = {"rich_text": [{"text": {"content": self._shorten_string(movie.plot)}}]}
        if movie.genres:
            genres = [{"name": genre} for genre in movie.genres if genre]
            if movie.is_series:
                genres.insert(0, {"name": "TV Series"})
            properties["Genre"] = {"multi_select": genres}
        return properties

    def _shorten_string(self, string: str, max_length: int = 1000) -> str:
        if len(string) > max_length:
            return string[:max_length-3] + "..."
        return string
