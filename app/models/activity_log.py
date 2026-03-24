from datetime import datetime
from app.database import db

# MongoDB collection reference
activity_logs_collection = db["activity_logs"]

# Helper function to insert a new log
async def create_activity_log(admin_id: str, action: str, description: str, target_user_id: str = None):
    log_entry = {
        "admin_id": admin_id,
        "action": action,
        "target_user_id": target_user_id,
        "description": description,
        "created_at": datetime.utcnow()
    }
    await activity_logs_collection.insert_one(log_entry)
    return log_entry