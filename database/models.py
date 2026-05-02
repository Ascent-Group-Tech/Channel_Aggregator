from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from datetime import datetime

#Таблиця де кожному донорському каналу присвоюється ункальний ID
class Pairs(Base):
    __tablename__ = "pairs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    source_msg_id: Mapped[int] = mapped_column(unique=True)
    target_msg_id: Mapped[int] = mapped_column(unique=True)

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
