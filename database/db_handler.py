from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from . import models
from database.database import get_db


def save_pair(source_id: int, target_id: int):
    with get_db() as db:
        try:
            pair = models.Pairs(
                source_msg_id=source_id,
                target_msg_id=target_id,
            )
            db.add(pair)
            db.commit()
            db.refresh(pair)

            return pair
        except IntegrityError:
            db.rollback()
            return None

def get_my_id_by_original(source_id: int):
    with get_db() as db:
        pair = (
            db.query(models.Pairs)
            .filter(models.Pairs.source_msg_id == source_id)
            .first()
        )

        if not pair:
            return None

        return pair.target_msg_id

def delete_pair(source_id: int):
    with get_db() as db:
        pair = (
            db.query(models.Pairs)
            .filter(models.Pairs.source_msg_id == source_id)
            .first()
        )

        if not pair:
            return False

        pair.is_deleted = True
        db.commit()
        return True

def get_last_seen_source_id() -> int:
    with get_db() as db:
        max_id = db.query(func.max(models.Pairs.source_msg_id)).scalar()
        return max_id or 0
