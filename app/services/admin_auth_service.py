from passlib.context import CryptContext
from datetime import datetime
from app.database import db
from app.core.jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

async def create_admin(admin):
    existing = await db.admins.find_one({"username": admin.username})
    if existing:
        return {"error": "Username already exists"}

    hashed_pw = hash_password(admin.password)
    new_admin = {
        "username": admin.username,
        "password_hash": hashed_pw,
        "role": admin.role,
        "created_at": datetime.utcnow()
    }
    await db.admins.insert_one(new_admin)
    return {"message": "Admin created successfully"}

async def login_admin(username: str, password: str):
    admin = await db.admins.find_one({"username": username})
    if not admin or not verify_password(password, admin["password_hash"]):
        return None
    token = create_access_token(admin["username"], admin["role"])
    return token