import os
from dotenv import load_dotenv

# Завантажуємо змінні з .env
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

if not API_ID or not API_HASH:
    raise ValueError("API_ID або API_HASH не знайдені в .env")

API_ID = int(API_ID)
API_HASH = str(API_HASH)

SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")

if not SOURCE_CHANNEL or not TARGET_CHANNEL:
    raise ValueError("SOURCE_CHENNEL or TARGET_CHENNEL не знайдені в .env")
