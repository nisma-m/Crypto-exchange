from pydantic import BaseModel

class AdminCreate(BaseModel):
    username: str
    password: str
    role: str

class AdminLogin(BaseModel):
    username: str
    password: str