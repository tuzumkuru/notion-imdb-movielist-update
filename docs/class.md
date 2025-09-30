# Class Diagram

This diagram shows the key classes in your application, their most important methods, and the relationships between them. It helps to understand the object-oriented structure of the code.

```mermaid
classDiagram
    class Updater {
        -notion_api: NotionAPI
        -imdb_adapter: IMDbAdapter
        +update_page(page: NotionPage)
        -_get_movie_from_page(page: NotionPage) Movie
        -_create_notion_properties(movie: Movie) dict
    }

    class NotionAPI {
        +get_empty_pages(database_id: str) list
        +update_page(page_id: str, properties: dict)
        +find_database_id(name: str) str
    }

    class IMDbAdapter {
        <<abstract>>
        +get_movie(movie_id: str) Movie
        +search_movie(title: str) Movie
    }

    class IMDbInfoAdapter {
        +get_movie(movie_id: str) Movie
        +search_movie(title: str) Movie
    }

    class Movie {
        <<dataclass>>
        title: str
        imdb_id: str
        director: str
        rating: float
        ...
    }

    class NotionPage {
        <<dataclass>>
        id: str
        title: str
        imdb_url: str
    }

    Updater o-- NotionAPI
    Updater o-- IMDbAdapter
    IMDbInfoAdapter --|> IMDbAdapter
    Updater ..> Movie : uses
    Updater ..> NotionPage : uses

```
