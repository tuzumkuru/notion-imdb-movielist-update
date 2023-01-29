import os
import sys
from pprint import pprint
from imdb import Cinemagoer

from notion_client import Client

class Movie:
    Name : str
    Address : str


def GetDatabaseId(database_name:str):
    results = notion.search(query=NOTION_DATABASE_NAME, filter=
       {
                "property": "object",
                "value":"database"
                }
    ).get("results")

    database_id = results[0]["id"]

    return database_id

def GetEmptyPages(database_id:int):
    missingPagesFilter = {
        "filter": {
            "and": [
                {
                    "or": [
                        {
                            "property": "Name",
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
                            "property": "Length [min]",
                            "number": {
                                "is_empty": True
                            }
                        },
                        {
                            "property": "Director",
                            "select": {
                                "is_empty": True
                            }
                        }
                    ]
                }
            ]
        }
    }

    return notion.databases.query(database_id=database_id, **missingPagesFilter).get("results")

def GetMovie(movie_name:str,movie_address:str):
    pass

def UpdatePage(page_id:int,movie:Movie):
    pass





if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        print("Could not load .env because python-dotenv not found.")
    else:
        load_dotenv()

    NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
    NOTION_DATABASE_NAME = os.getenv("NOTION_DATABASE_NAME", "")

    while NOTION_TOKEN == "":
        print("NOTION_TOKEN not found.")
        NOTION_TOKEN = input("Enter your integration token: ").strip()

    # Initialize the client
    notion = Client(auth=NOTION_TOKEN)

    # Retrieve the database based on its name
    database_id = GetDatabaseId(database_name=NOTION_DATABASE_NAME)

    pages = GetEmptyPages(database_id=database_id)

    # create an instance of the Cinemagoer class
    cinemagoer = Cinemagoer()

    movies = cinemagoer.search_movie(title="Back to the future")

    movie = cinemagoer.get_movie(movieID="0088763")

    print(movie['director'])

    print(database_id)

