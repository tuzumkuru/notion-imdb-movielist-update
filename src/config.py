import os
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_URL = os.getenv("NOTION_DATABASE_URL")
NOTION_DATABASE_NAME = os.getenv("NOTION_DATABASE_NAME")
