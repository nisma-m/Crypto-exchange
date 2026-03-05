from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    PROJECT_NAME: str = "Crypto Exchange Backend"

    MONGO_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "crypto_exchange"

    JWT_SECRET: str = "CHANGE_THIS_SECRET"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    BTC_NODE_URL: str = "http://localhost:8332"


settings = Settings()