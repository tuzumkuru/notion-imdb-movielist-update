import sys

import config
from imdbinfo_adapter import IMDbInfoAdapter
from logger import get_logger
from notion_api import NotionAPI
from exceptions import NotionAPIError, MovieNotFound
from imdb_adapter import IMDbAdapter
import re

logger = get_logger(__name__)

def get_genres(movie):
    genres = []
    if movie.genres:
        for genre in movie.genres:
            genres.append({'name': genre})
    return genres

def shorten_string(string, max_length=2000):
    if len(string) > max_length:
        return string[:max_length-3] + '...'
    else:
        return string

def get_id_from_url(url):
    pattern = r"tt(\d+)"
    match = re.search(pattern, url)
    if match:
        extracted_part = match.group(1)
        return extracted_part
    else:
        return None

def update_page(page: dict, imdb_adapter: IMDbAdapter, notion_api: NotionAPI):
    page_id = page["id"]
    try:
        page = notion_api.retrieve_page(page_id)

        imdb_link = page["properties"]["IMDB"]["url"]
        movie_title = ""
        if len(page["properties"]["Title"]["title"]) > 0:
            movie_title = page["properties"]["Title"]["title"][0]["text"]["content"]

        logger.info(f"Updating the movie: {movie_title}")

        movie = None
        if imdb_link:
            movie_id = get_id_from_url(imdb_link)
            if movie_id:
                movie = imdb_adapter.get_movie(movie_id)
        elif movie_title:
            movie = imdb_adapter.search_movie(movie_title)

        if not movie:
            raise MovieNotFound(f"Couldn't find the related movie for: {movie_title}")

        properties = {}
        updated_properties = []
        try:
            properties["Title"] = {'type': 'title', 'title': [{'type': 'text', 'text': {'content': movie.title}}]}
            updated_properties.append(f"Title: {movie.title}")
        except Exception as e:
            logger.error(f"Error updating Title for {movie_title}: {e}")

        try:
            director_name = "N/A"
            if not movie.is_series and movie.director:
                director_name = movie.director
            
            properties["Director"] = {'type': 'select', 'select': {'name': director_name}}
            updated_properties.append(f"Director: {director_name}")
        except Exception as e:
            logger.error(f"Error updating Director for {movie_title}: {e}")

        try:
            if movie.duration:
                properties["Duration [min]"] = {'type': 'number', 'number': movie.duration}
                updated_properties.append(f"Duration: {movie.duration} min")
        except Exception as e:
            logger.error(f"Error updating Duration for {movie_title}: {e}")

        try:
            if movie.rating:
                properties["IMDB Rating"] = {'type': 'number', 'number': movie.rating}
                updated_properties.append(f"IMDB Rating: {movie.rating}")
        except Exception as e:
            logger.error(f"Error updating IMDB Rating for {movie_title}: {e}")

        try:
            properties["IMDB"] = {'type': 'url', 'url': f"https://www.imdb.com/title/tt{movie.imdb_id}"}
            updated_properties.append(f"IMDB Link: https://www.imdb.com/title/tt{movie.imdb_id}")
        except Exception as e:
            logger.error(f"Error updating IMDB link for {movie_title}: {e}")

        try:
            if movie.plot:
                properties["Description"] = {'type': 'rich_text', 'rich_text':  [{'type': 'text', 'text': {'content': shorten_string(string=movie.plot, max_length=1000)}}]}
                updated_properties.append("Description updated")
        except Exception as e:
            logger.error(f"Error updating Description for {movie_title}: {e}")

        try:
            genres = get_genres(movie=movie)
            if movie.is_series:
                genres.insert(0, {"name": "TV Series"})
            properties["Genre"] = {'type': 'multi_select', 'multi_select': genres}
            updated_properties.append(f"Genres: {[g['name'] for g in genres]}")
        except Exception as e:
            logger.error(f"Error updating Genre for {movie_title}: {e}")

        notion_api.update_page(page_id=page_id, properties=properties)
        logger.info(f"Successfully updated {movie.title}:\n" + "\n".join(f"- {prop}" for prop in updated_properties))

    except (NotionAPIError, MovieNotFound) as e:
        logger.error(f"Failed to update: {e}")

def main():
    if not config.NOTION_TOKEN:
        logger.error("NOTION_TOKEN not found.")
        sys.exit(1)

    try:
        notion_api = NotionAPI(config.NOTION_TOKEN)
        imdb_adapter = IMDbInfoAdapter()

        DATABASE_ID = None
        if config.NOTION_DATABASE_URL:
            DATABASE_ID = notion_api.get_database_id_from_url(config.NOTION_DATABASE_URL)
        
        if not DATABASE_ID and config.NOTION_DATABASE_NAME:
            DATABASE_ID = notion_api.find_database_id(config.NOTION_DATABASE_NAME)

        if not DATABASE_ID:
            logger.error("Database can not be found.")
            sys.exit(1)

        pages = notion_api.get_empty_pages(database_id=DATABASE_ID)

        if pages:
            logger.info(f"Found {len(pages)} empty entries. Updating now...")
            for page in pages:
                update_page(page, imdb_adapter, notion_api)
        else:
            logger.info("No entries found")

        logger.info("Finished")

    except NotionAPIError as e:
        logger.error(f"A critical Notion API error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
