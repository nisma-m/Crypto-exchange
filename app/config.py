from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    PROJECT_NAME: str = "Crypto Exchange Backend"

    MONGO_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "crypto_exchange"

    # JWT (USE THIS EVERYWHERE)
    JWT_SECRET: str = "your_secret_key_here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

settings = Settings()