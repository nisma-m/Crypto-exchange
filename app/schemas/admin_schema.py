from pydantic import BaseModel
from typing import Optional

class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    role: str

class TransactionResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    type: str
    status: str

class SuspendUser(BaseModel):
    user_id: str
    reason: Optional[str] = None

class UserStatusUpdate(BaseModel):
    user_id: str
    status: str

class MessageResponse(BaseModel):
    message: str