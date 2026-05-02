import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from core.client import userbot, app
from logic.parser import parse_message
from database.db_handler import create_pair
from database.db_handler import SessionLocal


db = SessionLocal()


@app.on_message(filters.chat("channel_id"))
async def handle_new_post(client, message):

    # 1. Аналізує пост
    text = message.text or message.caption

    if not text:
        return "Немає тексту"

    # 2. Парсер перевіряє чи це продукт
    parsed = parse_message(text)

    if not parsed.is_product:
        return "Це не продукт"

    # 3. Створює новий текст
    new_text = f"{text}\n\n💰 {parsed.final_price}"

    # 4. Відправляє до каналу нового
    sent = await userbot.safe_send("YOUR_CHANNEL", new_text)

    if not sent:
        return "Проблема з базою"

    # 5. Записує до бази данних (source → target)
    create_pair(
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