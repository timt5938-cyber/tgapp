import logging
from io import BytesIO
from typing import Optional
from aiogram.types import BufferedInputFile
from .bot_instance import bot

logger = logging.getLogger(__name__)

class ConspectusDeliveryService:
    @staticmethod
    async def send_conspectus_pdf(
        chat_id: int,
        pdf_bytes: bytes,
        title: str = "Конспект",
        preview_bytes: Optional[bytes] = None
    ) -> bool:
        """
        Sends the synthesized PDF and an optional preview photo into the user's Telegram chat.
        """
        try:
            filename = f"{title.replace(' ', '_')[:30]}.pdf"
            doc_file = BufferedInputFile(pdf_bytes, filename=filename)

            caption = (
                f"📝 <b>Ваш готовый рукописный конспект</b>\n\n"
                f"📌 <i>Тема: {title}</i>\n"
                f"📎 Файл прикреплен ниже. Можно сразу распечатать или отправить преподавателю!"
            )

            # If preview image available, send photo first
            if preview_bytes:
                photo_file = BufferedInputFile(preview_bytes, filename="preview.jpg")
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=caption
                )
                # Send the document itself
                await bot.send_document(
                    chat_id=chat_id,
                    document=doc_file
                )
            else:
                await bot.send_document(
                    chat_id=chat_id,
                    document=doc_file,
                    caption=caption
                )

            logger.info("Delivered conspectus PDF to chat_id=%s", chat_id)
            return True
        except Exception as e:
            logger.error("Failed to deliver PDF to chat_id=%s: %s", chat_id, e)
            return False

delivery_service = ConspectusDeliveryService()
