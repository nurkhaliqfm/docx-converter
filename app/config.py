import os


class Settings:
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
    API_KEY = os.environ.get("CONVERT_API_KEY")
    ALLOWED_HOSTS = [
        h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()
    ]
    CORS_ORIGINS = [
        o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()
    ]
    MAX_UPLOAD_MB = 25
    SOFFICE_PATH = "soffice"

    @property
    def is_dev(self) -> bool:
        return self.ENVIRONMENT == "development"


settings = Settings()
