from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models


def save_pair(db: Session, source_id: int, target_id: int):
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
    

def get_my_id_by_original(db: Session, source_id: int):
    pair = (
        db.query(models.Pairs)
        .filter(models.Pairs.source_msg_id == source_id)
        .first()
    )

    if not pair:
        return None

    return pair.target_msg_id

def delete_pair(db: Session, source_id: int):
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
