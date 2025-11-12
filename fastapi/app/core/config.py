from decouple import config
import os


class Settings:
    # 环境配置
    ENVIRONMENT: str = config("ENVIRONMENT", default="development")
    DEBUG: bool = config("DEBUG", default=True, cast=bool)

    # 数据库配置
    DATABASE_URL: str = config("DATABASE_URL")
    DATABASE_POOL_SIZE: int = config("DATABASE_POOL_SIZE", default=20, cast=int)
    DATABASE_MAX_OVERFLOW: int = config("DATABASE_MAX_OVERFLOW", default=30, cast=int)
    DATABASE_POOL_RECYCLE: int = config("DATABASE_POOL_RECYCLE", default=3600, cast=int)

    # JWT配置
    SECRET_KEY: str = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7, cast=int)

    # 服务器配置
    HOST: str = config("HOST", default="0.0.0.0")
    PORT: int = config("PORT", default=8100, cast=int)
    WORKERS: int = config("WORKERS", default=4, cast=int)

    # 日志配置
    LOG_LEVEL: str = config("LOG_LEVEL", default="INFO")

    # AI服务配置
    BASE_URL: str = config("BASE_URL", default="http://localhost:8100")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"


settings = Settings()