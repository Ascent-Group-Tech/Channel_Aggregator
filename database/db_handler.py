from sqlalchemy.orm import Session
import models
from sqlalchemy.exc import IntegrityError


#Додає новий канал у базу даних
def add_channel(db: Session,channel_name: str):

    try:
        new_channel = models.Channels(channel_name=channel_name)
        
        db.add(new_channel)
        
        db.commit()
        db.refresh(new_channel)
        
        print(f"✅ Канал '{channel_name}' успішно додано!")
        return new_channel
    
    except IntegrityError:
        db.rollback()
        print(f"⚠️ Канал {channel_name} вже існує в базі.")
        return None
    
#Повертає ID нашого повідомлення з БД базуючись на ID повідомлення з донорського каналу    
def get_my_id_by_original(source_id : int, db: Session):

    our_message = db.query(models.TargetMessage).filter(models.TargetMessage.source_id == source_id).first()
    
    if not our_message:
        return None
    
    return our_message.message_id

#Видаляє наше повідомлення з БД(Насправді просто позначає наше повідомлення як видалене)
def delete_pair(source_id: int, db: Session):
    # 1. Знаходимо наш запис
    target = db.query(models.TargetMessage).filter(models.TargetMessage.source_id == source_id).first()
    
    if target:
        # 2. Оновлюємо статус замість фізичного видалення (це краще для історії!)
        target.status = "deleted"
        db.commit()
        return True
    return False