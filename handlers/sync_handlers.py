import asyncio
from hydrogram import Client, filters
from hydrogram.types import Message
from core.client import userbot, app
from logic.parser import parse_message
from database.db_handler import save_pair
from database.database import SessionLocal
from config import TARGET_CHANNEL, SOURCE_CHANNEL


db = SessionLocal()
channel=SOURCE_CHANNEL


@app.on_message(filters.chat(channel))
async def handle_new_post(client, message):

    # 1. Аналізує пост
    text = message.text or message.caption
   
    if not text:
        return 

    # 2. Парсер перевіряє чи це продукт
    parsed = parse_message(text)

    if not parsed.is_product:
        return 

    final_p = int(parsed.final_price) if parsed.final_price.is_integer() else parsed.final_price
    new_price_str = f"{parsed.emoji} {final_p}"
    new_text = text.replace(parsed.original_substring, new_price_str)
    new_caption = f"{new_text}"

    # 4. Відправляє до каналу нового
    sent = None

    if message.media_group_id:
        await asyncio.sleep(2.5)
        album = await client.get_media_group(message.chat.id, message.id)

        sent = await userbot.safe_send_album(
            TARGET_CHANNEL,
            album,
            new_caption
        )
    else:
        sent = await userbot.safe_copy(
            TARGET_CHANNEL,
            message,
            new_caption
        )

    # 5. Записує до бази данних (source → target)
    if sent:
        target_message_id = sent[0].id if isinstance(sent, list) else sent.id
        save_pair(
            db=db,
            source_id=message.id,
            target_id=target_message_id
        )
