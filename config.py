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
    max_upload_size_bytes: int = 5 * 1024 * 1024
    #default number of posts per page setting
    posts_per_page: int = 10

    #60 minutes before token is reseted
    reset_token_expire_minutes: int = 60
    # SMTP server host name
    mail_server: str= "localhost"
    #The port SMTP sever use 587 standard port 
    mail_port: int = 587
    #the user's username to authenticate with SMTP server
    mail_username: str = ""
    #the user's passwords to authenticate with SMTP server
    mail_password: SecretStr = SecretStr("")
    #sender(us) address that will appear in the from thier field of emails
    mail_from: str = "noreply@example.com"
    #tell aiosmtp when to use TLS encryption.
    #Without encryption, your SMTP password and the email itself (including the reset link) travel in plain text.
    mail_use_tls: bool = True
    #base URL to build reset password link - hardcode for securty reason - if take link directly from request, it can direct to hacker links
    frontend_url: str = "http://localhost:8000"

settings = Settings() #loaded from .env file