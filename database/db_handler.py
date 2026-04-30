from sqlalchemy.orm import Session
from .models import Channels
from sqlalchemy.exc import IntegrityError


#Додає новий канал у базу даних
def add_channel(db: Session,channel_name: str):

    try:
        new_channel = Channels(channel_name=channel_name)
        
        db.add(new_channel)
        
        db.commit()
        db.refresh(new_channel)
        
        print(f"✅ Канал '{channel_name}' успішно додано!")
        return new_channel
    
    except IntegrityError:
        db.rollback()
        print(f"⚠️ Канал {channel_name} вже існує в базі.")
        return None