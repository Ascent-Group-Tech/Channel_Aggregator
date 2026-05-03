from hydrogram.client import Client
from hydrogram.errors import FloodWait, RPCError, PeerIdInvalid, MessageIdInvalid, Unauthorized
from hydrogram.types import InputMediaPhoto, InputMediaVideo, Message
from database.db_handler import get_last_seen_source_id
import logging
from typing import Iterable
from config import API_ID, API_HASH, TARGET_CHANNEL
from logic.parser import updated_message, parse_message
from database.db_handler import save_pair
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not TARGET_CHANNEL:
    raise ValueError("Немає Target_Channel")

class UserBot:
    def __init__(self):
        self.app = Client(
            name="userbot",
                api_id=API_ID,
                api_hash=API_HASH,
                workdir="sessions"
        )

    async def start(self):
        try:
            await self.app.start()
            me = await self.app.get_me()
            logger.info(f"ЮзерБот запущено: {me.first_name}")
        except RPCError as e:
            logger.error(f"Помилка Telegram API {e}")
        except Exception as e:
            logger.error(f"Непередбачувальна помилка на старті {e}")

    async def stop(self):
        await self.app.stop()
        logger.info("ЮзерБот зупинений")

    async def safe_send(self, chat_id: int|str, text: str, **kwargs):
        try:
            return await self.app.send_message(chat_id, text, **kwargs)
        except FloodWait as e:
            logger.warning(f"FloodWait: Треба зачекати {e.value} секунд")

            wait_time = int(e.value) if isinstance(e.value, (int, str)) else 60
            await asyncio.sleep(wait_time)
            return await self.safe_send(chat_id, text, **kwargs)
        except PeerIdInvalid as e:
            logger.error(f"Я не бачив такого id: {e.value}")
            return None
        except MessageIdInvalid as e:
            logger.error("Наданого поста не існує: {e.value}")
            return None
        except Unauthorized as e:
            logger.error("Помилка з сессією Telegram: {e.value}")
            return None
        except Exception as e:
            logger.error(f"Невдалось надіслати повідомлення: {e}")
            return None

    async def safe_send_album(self, chat_id: int | str, original_messages: list[Message], caption: str):
        """
        Приймає список повідомлень з одного альбому, формує новий альбом
        і надсилає його з новим текстом (ціною).
        """

        media = []
        for i, msg in enumerate(original_messages):
            current_caption = caption if i == 0 else ""

            if msg.photo:
                media.append(InputMediaPhoto(msg.photo.file_id, caption=current_caption))
            elif msg.video:
                media.append(InputMediaVideo(msg.video.file_id, caption=current_caption))

        try:
            return await self.app.send_media_group(chat_id, media)
        except FloodWait as e:
            wait_time = int(e.value) if isinstance(e.value, (int, str)) else 60
            logger.warning(f"FloodWait: Чекаємо {wait_time} сек")
            await asyncio.sleep(wait_time)
            return await self.safe_send_album(chat_id, original_messages, caption)
        except Exception as e:
            logger.error(f"Помилка відправки альбому: {e}")
            return None

    async def safe_edit(self, chat_id: int | str, message_id: int, text: str, **kwargs):
        try:
            return await self.app.edit_message_text(chat_id, message_id, text, **kwargs)
        except Exception as e:
            logger.error(f"Помилка редагування: {e}")

    async def safe_delete(self, chat_id: int | str, message_id: int | Iterable[int]):
        try:
            return await self.app.delete_messages(chat_id, message_id)
        except Exception as e:
            logger.error(f"Помилка видалення {e}")
            return None

    async def safe_copy(self, chat_id: int | str, message: Message, new_text: str):
        """
        Універсальна функція: якщо це медіа (фото/відео) - копіює його з новим підписом.
        Якщо це просто текст - надсилає текст.
        """
        try:
            if message.media:
                # Копіюємо файл на серверах Telegram, просто міняємо підпис (caption)
                return await message.copy(chat_id, caption=new_text)
            else:
                # Якщо це голий текст
                return await self.app.send_message(chat_id, new_text)
        except FloodWait as e:
            wait_time = int(e.value) if isinstance(e.value, (int, str)) else 60
            logger.warning(f"FloodWait (copy): Треба зачекати {wait_time} секунд")
            await asyncio.sleep(wait_time)
            return await self.safe_copy(chat_id, message, new_text)
        except Exception as e:
            logger.error(f"Невдалось скопіювати повідомлення: {e}")
            return None

    async def send(self, chat_id: int | str,  message: Message, new_caption: str):
        """
        Головна супер функція для відправляння повідомлення правильно:
        if sended := userbot.send(message, new_caption):
            pass
        """
        sent = None
        if message.media_group_id:
            await asyncio.sleep(2.5)
            album = await self.app.get_media_group(message.chat.id, message.id)

            sent = await self.safe_send_album(
                chat_id,
                album,
                new_caption
            )
        else:
            sent = await self.safe_copy(
                chat_id,
                message,
                new_caption
            )
        return sent

    async def catch_up_history(self, chat_id: int | str):
        last_seen_id = get_last_seen_source_id()
        missed_messages = []

        history_generator = await self.app.get_chat_history(chat_id)
        if not history_generator:
            return

        async for message in history_generator:
            if message.id <= last_seen_id:
                break;
            missed_messages.append(message)

        for message in reversed(missed_messages):

            text = message.text or message.caption
            parsed = parse_message(text)
            if not parsed.is_product:
                continue

            new_caption = updated_message(parsed, text)

            if sended := await self.send(TARGET_CHANNEL, message, new_caption):
                target_message_id = sended[0].id if isinstance(sended, list) else sended.id
                save_pair(message.id, target_message_id)


userbot = UserBot()
app = userbot.app
