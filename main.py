import os
import sys
import re

from pprint import pprint
from imdbinfo import search_title, get_movie as get_imdb_movie
from notion_client import Client
from dotenv import load_dotenv

def find_database_id(database_name:str) -> str:
    results = notion.search(query=NOTION_DATABASE_NAME, filter={
        "property": "object",
        "value": "database"
    }).get("results")
    database_id = results[0]["id"]
    return database_id

def get_empty_pages(database_id:str):
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
    return notion.databases.query(database_id=database_id, **empty_page_filter).get("results")

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

def update_page_info(page):
    page = notion.pages.retrieve(page_id=page["id"])

    imdb_link = page["properties"]["IMDB"]["url"]
    movie_title = ""
    if len(page["properties"]["Title"]["title"]) > 0:
        movie_title = page["properties"]["Title"]["title"][0]["text"]["content"]

    print("Updating the movie " + str(movie_title))

    movie = None
    if imdb_link:
        movie_id = get_id_from_url(imdb_link)
        if movie_id:
            movie = get_imdb_movie(movie_id)
    elif movie_title:
        search_results = search_title(movie_title)
        if search_results.titles:
            movie = get_imdb_movie(search_results.titles[0].imdb_id)

    if movie:
        properties = {}
        try:
            properties["Title"] = {'type': 'title', 'title': [{'type': 'text', 'text': {'content': movie.title}}]}
        except Exception as e:
            print("Error: " + str(e))

        try:
            if not movie.is_series():
                if hasattr(movie, 'directors') and movie.directors:
                    properties["Director"] = {'type': 'select', 'select': {'name': movie.directors[0].name}}
        except Exception as e:
            print("Error: " + str(e))

        try:
            if movie.duration:
                properties["Duration [min]"] = {'type': 'number', 'number': movie.duration}
        except Exception as e:
            print("Error: " + str(e))

        try:
            if movie.rating:
                properties["IMDB Rating"] = {'type': 'number', 'number': movie.rating}
        except Exception as e:
            print("Error: " + str(e))

        try:
            properties["IMDB"] = {'type': 'url', 'url': f"https://www.imdb.com/title/tt{movie.imdb_id}"}
        except Exception as e:
            print("Error: " + str(e))

        try:
            if movie.plot:
                properties["Description"] = {'type': 'rich_text', 'rich_text':  [{'type': 'text', 'text': {'content': shorten_string(string=movie.plot, max_length=1000)}}]}
        except Exception as e:
            print("Error: " + str(e))

        try:
            genres = get_genres(movie=movie)
            if movie.is_series():
                genres.insert(0, {"name": "TV Series"})
            properties["Genre"] = {'type': 'multi_select', 'multi_select': genres}
        except Exception as e:
            print("Error: " + str(e))

        notion.pages.update(page_id=page["id"], properties=properties)
    else:
        print("Error: Couldn't find the related movie!")

def get_database_id_from_url(database_url:str) -> str:
    result = re.search(r"notion\.so/[^/]+/(\w+)", database_url)
    if result:
        result = result.group(1)
        if len(result) == 32:
            return result
    return None

if __name__ == "__main__":
    load_dotenv()

    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_DATABASE_URL = os.getenv("NOTION_DATABASE_URL")
    NOTION_DATABASE_NAME = os.getenv("NOTION_DATABASE_NAME")

    while not NOTION_TOKEN:
        print("NOTION_TOKEN not found.")
        NOTION_TOKEN = input("Enter your integration token: ").strip()

    notion = Client(auth=NOTION_TOKEN)

    DATABASE_ID = None
    if NOTION_DATABASE_URL:
        DATABASE_ID = get_database_id_from_url(NOTION_DATABASE_URL)
    
    if not DATABASE_ID and NOTION_DATABASE_NAME:
        DATABASE_ID = find_database_id(database_name=NOTION_DATABASE_NAME)

    while not DATABASE_ID:
        print("Database can not be found.")
        NOTION_DATABASE_URL = input("Enter your database url:").strip()
        DATABASE_ID = get_database_id_from_url(NOTION_DATABASE_URL)

    pages = get_empty_pages(database_id=DATABASE_ID)

    if pages:
        print(f"Found {len(pages)} empty entries. Updating now...")
        for page in pages:
            update_page_info(page)
    else:
        print("No entries found")

    print("Finished")