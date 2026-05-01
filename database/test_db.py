from database import dbEngine, Base, SessionLocal
import models
import db_handler

Base.metadata.create_all(bind=dbEngine)
db = SessionLocal()

#Додавання каналу
channel = db_handler.add_channel(db, "test_channel")
print(channel.id)

#Створення пари
result = db_handler.create_pair(
    db=db,
    channel_id=channel.id,
    text="Test product 100$",
    price=100,
    new_price=115,
    source_message_id_tg=1,
    target_message_id_tg=1000
)

print(result)

#Дістати ID
target_id = db_handler.get_target_id_by_source(result["source_id"], db)
print("TARGET TG ID:", target_id)


#Симуляція видалення
db_handler.delete_pair(result["source_id"], db)

#Перевірка

t = db.query(models.TargetMessage).filter_by(id=result["target_id"]).first()
print(t.is_deleted)

#Закриття сесії
db.close()