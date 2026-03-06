from pydantic import BaseModel

class UserStatusUpdate(BaseModel):
    user_id: str
    status: str