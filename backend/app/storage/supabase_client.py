import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from ..config import settings
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.client: Optional[Client] = None
        try:
            # Use anon key for standard operations
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
            logger.info("Connected to Supabase project at %s", settings.SUPABASE_URL)
        except Exception as e:
            logger.warning("Supabase connection warning: %s (falling back to local mode)", e)

    async def get_or_create_user(self, user_id: int, username: Optional[str] = None, first_name: Optional[str] = None) -> Dict[str, Any]:
        default_profile = {
            "id": user_id,
            "username": username or "",
            "first_name": first_name or "",
            "pen_style": "blue_ballpoint",
            "paper_style": "squared_5mm",
            "has_margins": True,
            "custom_gemini_key": None
        }
        if not self.client:
            return default_profile

        try:
            res = self.client.table("user_profiles").select("*").eq("id", user_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            
            # Create user
            insert_res = self.client.table("user_profiles").insert(default_profile).execute()
            return insert_res.data[0] if insert_res.data else default_profile
        except Exception as e:
            logger.error("Error in get_or_create_user: %s", e)
            return default_profile

    async def update_user_preferences(self, user_id: int, updates: Dict[str, Any]) -> bool:
        if not self.client:
            return False
        try:
            self.client.table("user_profiles").update(updates).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error("Error updating user preferences: %s", e)
            return False

    async def save_user_font(self, user_id: int, font_name: str, glyph_data: Dict[str, Any], storage_path: str) -> Optional[str]:
        if not self.client:
            return None
        try:
            # Set other fonts to inactive
            self.client.table("user_fonts").update({"is_active": False}).eq("user_id", user_id).execute()
            
            record = {
                "user_id": user_id,
                "font_name": font_name,
                "glyph_data": glyph_data,
                "storage_path": storage_path,
                "is_active": True
            }
            res = self.client.table("user_fonts").insert(record).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]["id"]
            return None
        except Exception as e:
            logger.error("Error saving user font: %s", e)
            return None

    async def get_active_user_font(self, user_id: int) -> Optional[Dict[str, Any]]:
        if not self.client:
            return None
        try:
            res = self.client.table("user_fonts").select("*").eq("user_id", user_id).eq("is_active", True).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except Exception as e:
            logger.error("Error getting active user font: %s", e)
            return None

    async def upload_asset(self, file_bytes: bytes, remote_filename: str, content_type: str = "application/pdf") -> Optional[str]:
        """Uploads a file to the conspectus-assets bucket and returns public URL."""
        if not self.client:
            return None
        try:
            bucket = settings.SUPABASE_BUCKET
            # Upload with overwrite
            self.client.storage.from_(bucket).upload(
                path=remote_filename,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            public_url = self.client.storage.from_(bucket).get_public_url(remote_filename)
            return public_url
        except Exception as e:
            logger.error("Error uploading to Supabase storage: %s", e)
            return None

    async def log_conspectus(self, user_id: int, title: str, mode: str, page_count: int, pdf_url: Optional[str] = None, preview_url: Optional[str] = None) -> Optional[str]:
        if not self.client:
            return None
        try:
            record = {
                "user_id": user_id,
                "title": title,
                "mode": mode,
                "page_count": page_count,
                "pdf_url": pdf_url,
                "preview_url": preview_url
            }
            res = self.client.table("conspectuses").insert(record).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]["id"]
            return None
        except Exception as e:
            logger.error("Error logging conspectus: %s", e)
            return None

supabase_service = SupabaseService()
