# Sequence Diagram

This diagram details the step-by-step logic of the main update process. It shows how the different objects in your code interact with each other in order to find and update a movie page in Notion.

```mermaid
sequenceDiagram
    participant Main as main.py
    participant Updater
    participant NotionAPI
    participant IMDbAdapter

    Main->>NotionAPI: get_empty_pages(db_id)
    NotionAPI-->>Main: Returns list of pages
    loop For each page
        Main->>Updater: update_page(page)
        Updater->>IMDbAdapter: search_movie(title) or get_movie(id)
        IMDbAdapter-->>Updater: Returns Movie object
        Updater->>NotionAPI: update_page(page_id, properties)
        NotionAPI-->>Updater: Confirms update
    end
```
