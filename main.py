from core.client import userbot
import asyncio
from pyrogram.sync import idle
import logging

#TODO: імпортувати хендлери
import handlers.sync_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
