import re
from notion_client import Client
from exceptions import NotionAPIError

class NotionAPI:
    def __init__(self, notion_token: str):
        self.client = Client(auth=notion_token)

    def find_database_id(self, database_name: str) -> str:
        try:
            results = self.client.search(query=database_name, filter={
                "property": "object",
                "value": "database"
            }).get("results")
            if not results:
                raise NotionAPIError(f"Database '{database_name}' not found.")
            return results[0]["id"]
        except Exception as e:
            raise NotionAPIError(f"Error finding database: {e}")

    def get_empty_pages(self, database_id: str) -> list:
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
        try:
            return self.client.databases.query(database_id=database_id, **empty_page_filter).get("results")
        except Exception as e:
            raise NotionAPIError(f"Error getting empty pages: {e}")

    def update_page(self, page_id: str, properties: dict):
        try:
            self.client.pages.update(page_id=page_id, properties=properties)
        except Exception as e:
            raise NotionAPIError(f"Error updating page: {e}")

    def retrieve_page(self, page_id: str) -> dict:
        try:
            return self.client.pages.retrieve(page_id=page_id)
        except Exception as e:
            raise NotionAPIError(f"Error retrieving page: {e}")

    @staticmethod
    def get_database_id_from_url(database_url: str) -> str | None:
        result = re.search(r"notion\.so/[^/]+/(\w+)", database_url)
        if result:
            result = result.group(1)
            if len(result) == 32:
                return result
        return None
