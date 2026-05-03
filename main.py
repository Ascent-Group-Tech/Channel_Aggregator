from core.client import userbot
import asyncio
from hydrogram import idle
import logging
import handlers.sync_handlers
from database.database import dbEngine, Base 
from config import SOURCE_CHANNEL

if not SOURCE_CHANNEL:
    raise ValueError("No target or source")

Base.metadata.create_all(bind=dbEngine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        await userbot.start()
        await userbot.catch_up_history(SOURCE_CHANNEL)
        await idle()
    except Exception as e:
        logger.error(f"Помилка {e}")
    finally:
        await userbot.stop()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Програма зупинена вручну")
