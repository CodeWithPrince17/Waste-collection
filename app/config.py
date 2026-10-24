from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Smart Waste Collection System"
    secret_key: str
    database_url: str = "sqlite:///./data/smart_waste.db"
    scheduler_enabled: bool = True

    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()