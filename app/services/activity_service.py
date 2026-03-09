from sqlalchemy.orm import Session
from app.models.activity_log import ActivityLog


def log_activity(db: Session, admin_id: int, action: str, description: str, target_user_id: int = None):

    log = ActivityLog(
        admin_id=admin_id,
        action=action,
        description=description,
        target_user_id=target_user_id
    )

    db.add(log)
    db.commit()