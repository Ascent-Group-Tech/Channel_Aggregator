from sqlalchemy import String, Text, Boolean, DateTime, Integer, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from .database import Base
from datetime import datetime

#Таблиця де кожному донорському каналу присвоюється ункальний ID
class Channel(Base):
    __tablename__ = "channels"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_name: Mapped[str] = mapped_column(Text, unique=True)

    #Цей рядок дозволяє ORM встановлювати зв'язки між Channel та SourceMessage
    source_messages: Mapped[list["SourceMessage"]] = relationship(back_populates="channel")

#Таблиця повідомлень каналу донора
class SourceMessage(Base):
    __tablename__ = "source_messages"

    #ID рядка в таблиці
    id: Mapped[int] = mapped_column(primary_key=True)

    #ID повідомлення та каналу в якому воно опубліковане
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    message_id_tg: Mapped[int] = mapped_column(index=True)
    
    #Інформація про повідомлення
    text: Mapped[str | None] = mapped_column(Text)
    price: Mapped[int | None] = mapped_column(Integer)

    #Визначаємо чи це повідомлення було видалене
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    channel: Mapped["Channel"] = relationship(back_populates="source_messages")
    target_messages: Mapped[list["TargetMessage"]] = relationship(back_populates="source_message")

    #Записуємо час коли ми створили та редагували рядок 
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("channel_id", "message_id_tg"),
    )


class TargetMessage(Base):
    __tablename__ = "target_messages"

    #ID рядка в таблиці
    id: Mapped[int] = mapped_column(primary_key=True)

    #ID повідомлення в таблиці з яким зв'язане наше повідомлення
    source_id: Mapped[int] = mapped_column(ForeignKey("source_messages.id"))
    
    #ID нашого повідомлення
    message_id_tg: Mapped[int] = mapped_column(index=True, unique=True)
    
    #Інформація про повідомлення
    text: Mapped[str | None] = mapped_column(Text)
    price: Mapped[int | None] = mapped_column(Integer)

    #Визначаємо чи це повідомлення було видалене
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    #Записуємо час коли ми створили та редагували рядок 
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),onupdate=func.now())

    source_message: Mapped["SourceMessage"] = relationship(back_populates="target_messages")