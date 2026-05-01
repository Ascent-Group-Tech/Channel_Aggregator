from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models


#Додає новий канал у базу даних
def add_channel(db: Session, channel_name: str):
    try:
        channel = models.Channel(channel_name=channel_name)

        db.add(channel)
        db.commit()
        db.refresh(channel)

        return channel

    except IntegrityError:
        db.rollback()
        return None
    
#Повертає ID нашого повідомлення з БД базуючись на ID повідомлення з донорського каналу    
def get_target_id_by_source(source_id: int, db: Session):
    target = (
        db.query(models.TargetMessage)
        .filter(models.TargetMessage.source_id == source_id)
        .first()
    )

    if not target:
        return None

    return target.message_id_tg

#Видаляє наше повідомлення з БД(Насправді просто позначає наше повідомлення як видалене)
def delete_pair(source_id: int, db: Session):
    target = (
        db.query(models.TargetMessage)
        .filter(models.TargetMessage.source_id == source_id)
        .first()
    )

    if not target:
        return False

    target.is_deleted = True
    db.commit()

    return True

#Додає повідомлення донора в таблицю SourceMessage та наше в таблицю TargetMessage
def create_pair(
    db: Session,
    channel_id: int,
    text: str,
    price: int,
    new_price: int,
    source_message_id_tg: int,
    target_message_id_tg: int
):
    try:
        # 1. створюємо source
        source = models.SourceMessage(
            channel_id=channel_id,
            message_id_tg=source_message_id_tg,
            text=text,
            price=price
        )

        db.add(source)
        db.flush()  # щоб отримати source.id

        # 2. створюємо target
        target = models.TargetMessage(
            source_id=source.id,
            message_id_tg=target_message_id_tg,
            text=text,
            price=new_price
        )

        db.add(target)
        db.commit()

        return {
            "source_id": source.id,
            "target_id": target.id
        }

    except Exception:
        db.rollback()
        raise

#Оновлює пару
def update_pair(
    db: Session,
    source_id: int,
    new_text: str | None = None,
    new_price: int | None = None
):
    source = (
        db.query(models.SourceMessage)
        .filter(models.SourceMessage.id == source_id)
        .first()
    )

    if not source:
        return False

    if new_text is not None:
        source.text = new_text

    if new_price is not None:
        source.price = new_price

    db.commit()
    return True