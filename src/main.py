import sys
from typing import List, Dict, Any

import config
from imdbinfo_adapter import IMDbInfoAdapter
from logger import get_logger
from notion_api import NotionAPI
from exceptions import NotionAPIError
from updater import Updater
from notion_page import NotionPage

logger = get_logger(__name__)

def _get_database_id(notion_api: NotionAPI) -> str | None:
    """Gets the database ID from the URL or by searching the database name."""
    if config.NOTION_DATABASE_URL:
        database_id = notion_api.get_database_id_from_url(config.NOTION_DATABASE_URL)
        if database_id:
            return database_id
    
    if config.NOTION_DATABASE_NAME:
        return notion_api.find_database_id(config.NOTION_DATABASE_NAME)
    
    return None

def _process_pages(pages: List[Dict[str, Any]], updater: Updater):
    """Processes a list of Notion pages."""
    if not pages:
        logger.info("No entries found to update.")
        return

    logger.info(f"Found {len(pages)} empty entries. Updating now...")
    for page_data in pages:
        title = None
        if page_data["properties"]["Title"]["title"]:
            title = page_data["properties"]["Title"]["title"][0]["text"]["content"]

        page = NotionPage(
            id=page_data["id"],
            title=title,
            imdb_url=page_data["properties"]["IMDB"]["url"]
        )
        updater.update_page(page)

def main():
    if not config.NOTION_TOKEN:
        logger.error("NOTION_TOKEN not found.")
        sys.exit(1)

    try:
        notion_api = NotionAPI(config.NOTION_TOKEN)
        imdb_adapter = IMDbInfoAdapter()
        updater = Updater(notion_api, imdb_adapter)

        database_id = _get_database_id(notion_api)
        if not database_id:
            logger.error("Database could not be found. Please check your configuration.")
            sys.exit(1)

        pages = notion_api.get_empty_pages(database_id=database_id)
        _process_pages(pages, updater)

        logger.info("Finished")

    except NotionAPIError as e:
        logger.error(f"A critical Notion API error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
