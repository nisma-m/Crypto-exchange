from pydantic import BaseModel


class WalletCreateRequest(BaseModel):
    user_id: str
    currency: str