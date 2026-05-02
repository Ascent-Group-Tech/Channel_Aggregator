import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from core.client import userbot, app
from logic.parser import parse_message
from database.db_handler import save_pair
from database.db_handler import SessionLocal
from config import TARGET_CHANNEL


db = SessionLocal()
channel=TARGET_CHANNEL

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

    # 3. Створює новий текст
    new_caption = f"{text}\n\n💰 {parsed.final_price}"

    # 4. Відправляє до каналу нового
    sent = None

    if message.media_group_id:

        album = await client.get_media_group(message.chat.id, message.id)

        sent = await userbot.safe_send_album(
            TARGET_CHANNEL,
            album,
            new_caption
        )

    elif message.photo or message.video:

        sent = await userbot.app.send_photo(
            TARGET_CHANNEL,
            message.photo.file_id if message.photo else message.video.file_id,
            caption=new_caption
        )

    else:
        sent = await userbot.safe_send(
            TARGET_CHANNEL,
            new_caption
        )

    # 5. Записує до бази данних (source → target)
    save_pair(
        db=db,
        channel_id=1,
        text=text,
        price=parsed.price,
        new_price=parsed.final_price,
        source_message_id_tg=message.id,
        target_message_id_tg=sent.id
    )
    


async def main():
    await userbot.start()
    await asyncio.Event().wait()


asyncio.run(main())