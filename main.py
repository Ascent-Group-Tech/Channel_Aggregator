from core.client import userbot
import asyncio
from hydrogram import idle
import logging
import handlers.sync_handlers
from database.database import dbEngine, Base, get_db
from database.database import DB_PATH

Base.metadata.create_all(bind=dbEngine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import os

print(f"--- DEBUG INFO ---")
print(f"Поточна робоча директорія (CWD): {os.getcwd()}")
print(f"Шлях до БД: {DB_PATH}")
print(f"Чи існує папка для БД? {os.path.exists(DB_PATH.parent)}")
print(f"Чи є права на запис у папку? {os.access(DB_PATH.parent, os.W_OK)}")
print(f"------------------")
async def main():
    try:
        await userbot.start()
        await idle()
    except Exception as e:
        logger.error(f"Помилка {e}")
    finally:
        await userbot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Програма зупинена вручну")
