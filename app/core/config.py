import os
import json
import logging
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from eth_utils import is_address, to_checksum_address
from app.core.exceptions import InvalidAddressError, ConfigurationError

load_dotenv()

logger = logging.getLogger(__name__)

class Settings(BaseModel):
    ACCOUNT_ADDRESS: str = Field(default_factory=lambda: os.getenv("ACCOUNT_ADDRESS", ""))

    USERS_LISTENED: list[str] = Field(default_factory=list)
    
    @field_validator('ACCOUNT_ADDRESS')
    @classmethod
    def validate_account_address(cls, v: str) -> str:
        if not v:
            return v
        if not is_address(v):
            raise InvalidAddressError(v, "Doit être une adresse Ethereum valide (format 0x...)")
        return to_checksum_address(v)

    TELEGRAM_BOT_TOKEN: str = Field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    TELEGRAM_CHAT_ID: str = Field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))

    SECRET_KEY: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", ""))
    API_PORT: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    API_HOST: str = Field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    
    API_KEY: str = Field(default_factory=lambda: os.getenv("API_KEY", ""))
    ALLOWED_ORIGINS: list[str] = Field(default_factory=list)
    TRADING_ENABLED: bool = Field(default_factory=lambda: os.getenv("TRADING_ENABLED", "true").lower() in ("true", "1", "yes"))

    def __init__(self, **data):
        super().__init__(**data)

        raw_users = os.getenv("USERS_LISTENED", "[]")
        try:
            self.USERS_LISTENED = json.loads(raw_users)
        except Exception as e:
            raise ConfigurationError("USERS_LISTENED", f"Doit être un JSON valide, ex: ['0xabc', '0xdef']. Erreur: {e}")
        
        for addr in self.USERS_LISTENED:
            if not is_address(addr):
                raise InvalidAddressError(addr, "Les adresses dans USERS_LISTENED doivent être valides")
        
        self.USERS_LISTENED = [to_checksum_address(addr) for addr in self.USERS_LISTENED]

        raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
        self.ALLOWED_ORIGINS = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
        
        if not self.API_KEY:
            logger.warning("API_KEY non défini. L'authentification sera désactivée (non recommandé en production).")
        elif len(self.API_KEY) < 32:
            raise ConfigurationError("API_KEY", "Doit contenir au minimum 32 caractères pour la sécurité")
        
        if self.TRADING_ENABLED and not self.SECRET_KEY:
            raise ConfigurationError("SECRET_KEY", "Doit être défini dans .env lorsque TRADING_ENABLED=true")
        
        if not self.SECRET_KEY:
            logger.info("Mode read-only activé (SECRET_KEY non défini). Les opérations de trading seront désactivées.")

settings = Settings()