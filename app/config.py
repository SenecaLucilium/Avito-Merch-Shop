from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Avito Merch Shop"
    VERSION: str = "1.0.0"

    DATABASE_URL: str = "postgresql://postgres:password@db:5432/shop"

    JWT_SECRET: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    INITIAL_COINS: int = 1000
    
    class Config:
        env_file = ".env"

settings = Settings()