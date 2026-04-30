import os
from dotenv import load_dotenv

# Завантажуємо змінні з .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")
MARKUP = float(os.getenv("PERCENT_MARKUP")) / 100
