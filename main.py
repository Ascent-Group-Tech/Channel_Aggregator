from core.client import userbot
import asyncio
from hydrogram import idle
import logging
import handlers.sync_handlers
from database.database import dbEngine, Base, get_db
from core.client import app

Base.metadata.create_all(bind=dbEngine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import os

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
        loop = asyncio.get_event_loop()
        # Запускаємо нашу головну функцію саме в ньому
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Програма зупинена вручну")
