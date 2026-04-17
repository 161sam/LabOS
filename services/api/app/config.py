from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.env', '../../.env'),
        extra='ignore',
    )

    app_name: str = 'LabOS API'
    database_url: str = 'sqlite:///./labos.db'
    redis_url: str = 'redis://localhost:6379/0'
    abrain_base_url: str = 'http://abrain:8080'
    storage_path: str = 'storage'


settings = Settings()
