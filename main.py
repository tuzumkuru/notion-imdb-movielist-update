import re
import sys
from notion_client import Client

import config
from imdbinfo_adapter import IMDbInfoAdapter
from logger import get_logger

logger = get_logger(__name__)

def find_database_id(database_name:str, notion_client: Client) -> str:
    results = notion_client.search(query=database_name, filter={
        "property": "object",
        "value": "database"
    }).get("results")
    database_id = results[0]["id"]
    return database_id

def get_empty_pages(database_id:str, notion_client: Client):
    empty_page_filter = {
        "filter": {
            "and": [
                {
                    "or": [
                        {
                            "property": "Title",
                            "title": {
                                "is_not_empty": True
                            }
                        },
                        {
                            "property": "IMDB",
                            "url": {
                                "is_not_empty": True
                            }
                        }
                    ]
                },
                {
                    "or": [
                        {
                            "property": "Duration [min]",
                            "number": {
                                "is_empty": True
                            }
                        },
                        {
                            "property": "Director",
                            "select": {
                                "is_empty": True
                            }
                        },
                        {
                            "property": "IMDB",
                            "url": {
                                "is_empty": True
                            }
                        }
                    ]
                }
            ]
        }
    }
    return notion_client.databases.query(database_id=database_id, **empty_page_filter).get("results")

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

def update_page_info(page, imdb_adapter, notion_client: Client):
    page = notion_client.pages.retrieve(page_id=page["id"])

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

    if movie:
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

        notion_client.pages.update(page_id=page["id"], properties=properties)
        logger.info(f"Successfully updated {movie.title}:\n" + "\n".join(f"- {prop}" for prop in updated_properties))
    else:
        logger.error(f"Couldn't find the related movie for: {movie_title}")

def get_database_id_from_url(database_url:str) -> str:
    result = re.search(r"notion\.so/[^/]+/(\w+)", database_url)
    if result:
        result = result.group(1)
        if len(result) == 32:
            return result
    return None

def main():
    if not config.NOTION_TOKEN:
        logger.error("NOTION_TOKEN not found.")
        sys.exit(1)

    notion = Client(auth=config.NOTION_TOKEN)
    imdb_adapter = IMDbInfoAdapter()

    DATABASE_ID = None
    if config.NOTION_DATABASE_URL:
        DATABASE_ID = get_database_id_from_url(config.NOTION_DATABASE_URL)
    
    if not DATABASE_ID and config.NOTION_DATABASE_NAME:
        DATABASE_ID = find_database_id(database_name=config.NOTION_DATABASE_NAME, notion_client=notion)

    if not DATABASE_ID:
        logger.error("Database can not be found.")
        sys.exit(1)

    pages = get_empty_pages(database_id=DATABASE_ID, notion_client=notion)

    if pages:
        logger.info(f"Found {len(pages)} empty entries. Updating now...")
        for page in pages:
            update_page_info(page, imdb_adapter, notion_client=notion)
    else:
        logger.info("No entries found")

    logger.info("Finished")

if __name__ == "__main__":
    main()