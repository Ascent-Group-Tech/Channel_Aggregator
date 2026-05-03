import asyncio
from hydrogram import Client, filters
from hydrogram.types import Message
from core.client import userbot, app
from logic.parser import parse_message, updated_message
from database.db_handler import save_pair, get_my_id_by_original, check_exists_source_id
from database.database import SessionLocal
from config import TARGET_CHANNEL, SOURCE_CHANNEL


db = SessionLocal()
channel=SOURCE_CHANNEL

if(not TARGET_CHANNEL or not SOURCE_CHANNEL):
    raise ValueError("No target or source")


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

    
    new_caption = updated_message(parsed, text);

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

@app.on_edited_message(filters.chat(channel))
async def handle_edit_post(client: Client, message: Message):
    our_message_id = get_my_id_by_original(db, message.id)
    if not our_message_id:
        return

    parsed = parse_message(message.text)
    if not parsed.is_product:
        return

    new_caption = updated_message(parsed, message.text)
    await userbot.safe_edit(TARGET_CHANNEL, our_message_id, message.text);
