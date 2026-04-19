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
    abrain_use_stub: bool = True
    abrain_timeout_seconds: float = 8.0
    storage_path: str = 'storage'
    photo_max_upload_bytes: int = 8 * 1024 * 1024
    public_web_base_url: str = 'http://localhost:3000'
    public_api_base_url: str = 'http://localhost:8000'
    auth_secret_key: str = 'change-me-for-production'
    auth_cookie_name: str = 'labos_session'
    auth_cookie_secure: bool = False
    auth_token_ttl_hours: int = 12
    bootstrap_admin_username: str = 'admin'
    bootstrap_admin_password: str = 'labosadmin'
    bootstrap_admin_display_name: str = 'LabOS Admin'
    bootstrap_admin_email: str | None = 'admin@local.labos'
    mqtt_enabled: bool = False
    mqtt_broker_host: str = 'localhost'
    mqtt_broker_port: int = 1883
    mqtt_client_id: str = 'labos-api'
    mqtt_topic_prefix: str = 'labos'
    mqtt_publish_commands: bool = True
    scheduler_enabled: bool = True
    scheduler_tick_seconds: float = 5.0


settings = Settings()
