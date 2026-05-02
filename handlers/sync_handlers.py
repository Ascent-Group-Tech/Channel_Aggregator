import asyncio
from hydrogram import Client, filters
from core.client import userbot, app
from logic.parser import parse_message
from database.db_handler import save_pair
from database.database import SessionLocal # Імпортуємо фабрику сесій
from config import TARGET_CHANNEL, SOURCE_CHANNEL

@app.on_message(filters.chat(SOURCE_CHANNEL))
async def handle_new_post(client, message):
    text = message.text or message.caption
    if not text:
        return 

    parsed = parse_message(text)
    if not parsed.is_product:
        return 

    old_price_str = f"{parsed.price}"
    new_price_str = f"{parsed.final_price}"
    new_text = text.replace(old_price_str, new_price_str)
    new_caption = f"{new_text}\n\n💰"

    sent_msg = None

    try:
        if message.media_group_id:
            album = await client.get_media_group(message.chat.id, message.id)
            # safe_send_album повертає List[Message]
            sent_list = await userbot.safe_send_album(
                TARGET_CHANNEL, 
                album, 
                new_caption
            )
            if sent_list:
                sent_msg = sent_list[0] # Беремо перше повідомлення з альбому
        else:
            sent_msg = await userbot.safe_send(
                TARGET_CHANNEL, 
                new_caption
            )

        if sent_msg:
            with SessionLocal() as db: # Контекстний менеджер сам закриє сесію
                save_pair(
                    db=db,
                    source_id=message.id,
                    target_id=sent_msg.id,
                )
                print(f"✅ Успішно: {message.id} -> {sent_msg.id}")

    except Exception as e:
        print(f"❌ Помилка в хендлері: {e}")
