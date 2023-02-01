import os
import sys

from pprint import pprint
from imdb import Cinemagoer
from imdb import Movie
from notion_client import Client


def FindDatabaseId(database_name:str) -> str:
    results = notion.search(query=NOTION_DATABASE_NAME, filter=
       {
                "property": "object",
                "value":"database"
                }   
    ).get("results")

    database_id = results[0]["id"]

    return database_id

def GetEmptyPages(database_id:str):
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

    return notion.databases.query(database_id=database_id, **missingPagesFilter).get("results")

def GetGenres(movie:Movie.Movie):    
    genres = []
    if len(movie["genres"]) > 0:        
        for genre in movie["genres"]:
            genres.append({'name': genre})
    return genres

def shorten_string(string, max_length=2000):
    if len(string) > max_length:
        return string[:max_length-3] + '...'
    else:
        return string

def UpdatePage(page):    
    # Retreive the page from API 
    page = notion.pages.retrieve(page_id=page["id"])

    # Get the Movie Title and IMDB Links
    imdb_link = page["properties"]["IMDB"]["url"]
    movie_title = page["properties"]["Name"]["title"][0]["text"]["content"]

    print("Updating the movie " + str(movie_title))

    # Search for the movie in IMDB
    if imdb_link:
        movie_id = imdb_link.rstrip('/').split('/')[-1][2:]
        movie = GetMovie(movie_id=movie_id) 
    else:
        movie = GetMovie(movie_title=movie_title)

    if movie != None:
        # Update Page info with the IMDB data
        try:
            page["properties"]["Name"]["title"] = [{'type': 'text','text': {'content': movie["title"]}}]
        except Exception as e:
            print("Error: " + str(e))

        try:
            if movie['kind']=="tv series":
                page["properties"]["Director"]["select"] = {'name': movie["writer"][0]["name"]}
            else:
                page["properties"]["Director"]["select"] = {'name': movie["director"][0]["name"]}
        except Exception as e:
            print("Error: " + str(e))
            page["properties"]["Director"]["select"] = {'name': "-"}

        try:
             page["properties"]["Length [min]"]["number"] = int(movie["runtimes"][0])
        except Exception as e:
            print("Error: " + str(e))

        try:
            page["properties"]["IMDB Rating"]["number"] = movie["rating"]
        except Exception as e:
            print("Error: " + str(e))

        try:
            page["properties"]["IMDB"] = {'type': 'url','url': "https://www.imdb.com/title/tt" + str(movie.movieID)}
        except Exception as e:
            print("Error: " + str(e))
        try:
            page["properties"]["Description"]["rich_text"] =  [{'type': 'text','text': {'content': shorten_string(string=movie.summary(),max_length=1000)}}]
        except Exception as e:
            print("Error: " + str(e))
        
        try:
            genres = GetGenres(movie=movie)
            if(movie['kind']=="tv series"):
                genres.insert(0,{"name":"TV Series"})
            page["properties"]["Genre"]["multi_select"] = genres
            pass # # page["properties"]["Genre"]["multi_select"] = [{'name': 'Adventure'},{'name': 'Comedy'},{'name': 'Sci-Fi'}] # movie["genres"] = ['Adventure', 'Comedy', 'Sci-Fi']
        except Exception as e:
            print("Error: " + str(e))

        # Save the page at Notion
        notion.pages.update(page_id=page["id"],**page)
    

def GetMovie(movie_title:str="",movie_id:str="") -> Movie.Movie: 
    result = None

    if movie_id != "":
        try :
            result = cinemagoer.get_movie(movieID=movie_id)
        except:
            pass
    
    if movie_title != "":
        movies = cinemagoer.search_movie(title=movie_title)
        for movie in movies:
            if movie["title"] == movie_title:
                return GetMovie(movie_id=movie.getID())                

    return  result

    



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

    # Initialize the Notion Client and Cinemagoer
    notion = Client(auth=NOTION_TOKEN)
    cinemagoer = Cinemagoer()

    # Retrieve the database ID based on its name
    database_id = FindDatabaseId(database_name=NOTION_DATABASE_NAME)

    # Retrieve empty pages
    pages = GetEmptyPages(database_id=database_id)    

    # Fill in empty pages
    if pages != None and pages !=  []:
        print("Found " + str(len(pages)) + " empty entries. Updating now...")
        for x in pages:
            UpdatePage(x)
    else:
        print("No entries found")

    print("Succesfull")

