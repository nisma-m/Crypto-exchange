from datetime import datetime, timedelta
from jose import jwt
from app.config import settings


def create_access_token(user_id: str):

    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow()
        + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token