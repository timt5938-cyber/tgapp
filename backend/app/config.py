import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env") if (ROOT_DIR / ".env").exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = "8941440413:AAHQob9S6KPZBPaJS3czdkY4pCM3rB68Nmc"
    
    # Gemini AI
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Supabase
    SUPABASE_URL: str = "https://faxtkubhxjesghpduiba.supabase.co"
    SUPABASE_KEY: str = "sb_publishable_OS78OrMo24Lj6D--fIv_YA_qLftDfK3"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZheHRrdWJoeGplc2docGR1aWJhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk5NzEwMjksImV4cCI6MjEwNTU0NzAyOX0.LLMR5xW3Fq98UyJBnJ1KIrjY-Rc_D1h3X9LiDsUWJa8"
    SUPABASE_BUCKET: str = "conspectus-assets"

    # Web & Mini App
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    MINI_APP_URL: str = "http://localhost:8000"

    # Paths
    BASE_DIR: Path = BASE_DIR
    ROOT_DIR: Path = ROOT_DIR
    STORAGE_DIR: Path = Path("/tmp/storage") if os.environ.get("VERCEL") else (ROOT_DIR / "storage")
    PRESETS_DIR: Path = BASE_DIR / "static" / "presets"
    TEMPLATES_DIR: Path = BASE_DIR / "static" / "templates"

settings = Settings()

# Ensure directories exist safely
try:
    settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    settings.PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    settings.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

