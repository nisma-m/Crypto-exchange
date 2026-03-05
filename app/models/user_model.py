from datetime import datetime
import uuid


def create_user_document(email: str, password: str, twofa_secret: str):

    user_id = f"USR_{uuid.uuid4().hex[:10]}"

    return {
        "user_id": user_id,

        "email": email,
        "password": password,

        "twofa_secret": twofa_secret,
        "twofa_enabled": False,

        "kyc_verified": False,

        "withdraw_whitelist": [],

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }