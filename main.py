import sys

import config
from imdbinfo_adapter import IMDbInfoAdapter
from logger import get_logger
from notion_api import NotionAPI
from exceptions import NotionAPIError
from updater import Updater
from notion_page import NotionPage

logger = get_logger(__name__)

def main():
    if not config.NOTION_TOKEN:
        logger.error("NOTION_TOKEN not found.")
        sys.exit(1)

    try:
        notion_api = NotionAPI(config.NOTION_TOKEN)
        imdb_adapter = IMDbInfoAdapter()
        updater = Updater(notion_api, imdb_adapter)

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
            for page_data in pages:
                title = None
                if len(page_data["properties"]["Title"]["title"]) > 0:
                    title = page_data["properties"]["Title"]["title"][0]["text"]["content"]

                page = NotionPage(
                    id=page_data["id"],
                    title=title,
                    imdb_url=page_data["properties"]["IMDB"]["url"]
                )
                updater.update_page(page)
        else:
            logger.info("No entries found")

        logger.info("Finished")

    except NotionAPIError as e:
        logger.error(f"A critical Notion API error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()