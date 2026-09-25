from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FlowForge"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str
    REDIS_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_JOB_EVENTS_TOPIC: str = "job-events"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()