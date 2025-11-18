import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    ACCOUNT_ADDRESS: str = Field(default_factory=lambda: os.getenv("ACCOUNT_ADDRESS", ""))
    SECRET_KEY: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", ""))
    
    API_PORT: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    API_HOST: str = Field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))

    def __init__(self, **data):
        super().__init__(**data)
        if not self.ACCOUNT_ADDRESS or not self.SECRET_KEY:
            raise ValueError("Les variables d'environnement ACCOUNT_ADDRESS et SECRET_KEY doivent être définies.")


try:
    settings = Settings()
except ValueError as e:
    print(f"Erreur de configuration: {e}")
    settings = Settings(ACCOUNT_ADDRESS="", SECRET_KEY="")