class MovieNotFound(Exception):
    """Raised when a movie cannot be found in the database."""
    pass

class NotionAPIError(Exception):
    """Raised for errors related to the Notion API."""
    pass
