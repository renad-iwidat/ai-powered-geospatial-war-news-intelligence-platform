import os
from dotenv import load_dotenv

# تحميل ملف .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
NEWS_VIEW_NAME = os.getenv("NEWS_VIEW_NAME", "vw_news_feed")
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "2"))
MAX_SNAPSHOT_LIMIT = int(os.getenv("MAX_SNAPSHOT_LIMIT", "200"))