import logging
from typing import Optional, List, Union
from google import genai
from google.genai import types
from ..config import settings
from .prompts import STUDENT_CONSPECTUS_SYSTEM_PROMPT, VERBATIM_CLEANUP_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        pass

    def _get_client(self, custom_key: Optional[str] = None) -> Optional[genai.Client]:
        key = custom_key or settings.GEMINI_API_KEY
        if not key:
            return None
        try:
            return genai.Client(api_key=key)
        except Exception as e:
            logger.error("Failed to initialize Gemini Client: %s", e)
            return None

    async def generate_conspectus_text(
        self,
        raw_text: Optional[str] = None,
        images_bytes: Optional[List[tuple[bytes, str]]] = None, # (bytes, mime_type)
        audio_bytes: Optional[tuple[bytes, str]] = None,        # (bytes, mime_type)
        mode: str = "smart",
        custom_key: Optional[str] = None
    ) -> str:
        client = self._get_client(custom_key)
        
        # Fallback if no Gemini key configured yet
        if not client:
            logger.warning("No Gemini API key available. Using local rule-based formatter.")
            return self._fallback_formatter(raw_text or "Лекция без текста", mode)

        try:
            system_instruction = (
                STUDENT_CONSPECTUS_SYSTEM_PROMPT 
                if mode == "smart" 
                else VERBATIM_CLEANUP_SYSTEM_PROMPT
            )

            contents = []

            # Add images if provided (multimodal slide / textbook analysis)
            if images_bytes:
                for img_data, mime in images_bytes:
                    contents.append(types.Part.from_bytes(data=img_data, mime_type=mime))

            # Add audio if provided (lecture speech transcription & note-taking)
            if audio_bytes:
                audio_data, mime = audio_bytes
                contents.append(types.Part.from_bytes(data=audio_data, mime_type=mime))

            # Add text prompt/input
            if raw_text:
                contents.append(raw_text)
            elif not contents:
                contents.append("Составь краткий конспект по теме.")

            # Call Gemini
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3 if mode == "smart" else 0.1,
                )
            )

            if response and response.text:
                return response.text.strip()
            else:
                return self._fallback_formatter(raw_text or "", mode)

        except Exception as e:
            logger.error("Gemini API call failed: %s. Falling back to local formatting.", e)
            return self._fallback_formatter(raw_text or "", mode)

    def _fallback_formatter(self, text: str, mode: str) -> str:
        """Local rule-based fallback when Gemini API key is not supplied."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return "Тема: Конспект лекции\n\n1. Введение в тему\n- Основные понятия и определения.\n[ВАЖНО] Главное правило темы.\n[ФОРМУЛА] F = m * a\n- Заключение и выводы."

        title = lines[0] if len(lines[0]) < 60 else "Тема: Конспект лекции"
        body = lines[1:] if len(lines[0]) < 60 else lines

        formatted = [f"Тема: {title}", ""]
        for idx, line in enumerate(body, 1):
            if line.endswith(":") or len(line) < 30:
                formatted.append(f"\n{idx}. {line}")
            else:
                formatted.append(f"- {line}")
        
        return "\n".join(formatted)

gemini_service = GeminiService()
