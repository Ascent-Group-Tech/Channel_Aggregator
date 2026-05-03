import asyncio
from hydrogram import Client, filters
from hydrogram.types import Message
from core.client import userbot, app
from logic.parser import parse_message, updated_message
from database.db_handler import save_pair, get_my_id_by_original, delete_pair
from config import TARGET_CHANNEL, SOURCE_CHANNEL


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


    # 5. Відправляємо та Записує до бази данних (source → target)
    if sent := await userbot.send(TARGET_CHANNEL, message, new_caption):
        target_message_id = sent[0].id if isinstance(sent, list) else sent.id
        save_pair(
            source_id=message.id,
            target_id=target_message_id
        )

@app.on_edited_message(filters.chat(channel))
async def handle_edit_post(client: Client, message: Message):
    our_message_id = get_my_id_by_original(message.id)
    if not our_message_id:
        return

    text = message.text or message.caption
    parsed = parse_message(text)
    if not parsed.is_product:
        return

    new_caption = updated_message(parsed, text)
    await userbot.safe_edit(TARGET_CHANNEL, our_message_id, new_caption);

@app.on_deleted_messages(filters.chat(channel))
async def handle_delete_post(client: Client, messages: list[Message]):

    for message in messages:
        our_message_id = get_my_id_by_original(message.id)
        if not our_message_id:
            continue
    
        text = message.text or message.caption
        parsed = parse_message(text)
        if not parsed.is_product:
            continue
        await userbot.safe_delete(TARGET_CHANNEL, message.id)
        delete_pair(message.id)

