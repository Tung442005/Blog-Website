#Later Ask how would the python-dotenv work instead of pydantic-settings
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #This line tell pydantic where to find the sources proatively --> then validate those sources --> in this case is .env files
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding="utf-8"
    )

    secret_key: SecretStr
    algorithm: str= "HS256"
    access_token_expire_minutes: int= 30

settings = Settings() #loaded from .env file