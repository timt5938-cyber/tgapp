import base64
import cv2
import numpy as np
import logging
from io import BytesIO
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..gemini.client import gemini_service
from ..rendering.handwriting_engine import handwriting_engine
from ..rendering.pdf_builder import pdf_builder
from ..rendering.paper_canvas import paper_canvas
from ..cv.sheet_detector import sheet_detector
from ..cv.glyph_extractor import glyph_extractor
from ..storage.supabase_client import supabase_service
from ..bot.delivery import delivery_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["studio"])

class PreviewRequest(BaseModel):
    text: str
    paper_style: str = "squared_5mm"
    has_margins: bool = True
    pen_color: str = "blue_ballpoint"
    font_preset: str = "marck_script"
    jitter: float = 1.0
    slant: float = 1.0
    humanize: bool = True

class GenerateRequest(BaseModel):
    user_id: int
    text: Optional[str] = None
    mode: str = "smart" # "smart" or "verbatim"
    paper_style: str = "squared_5mm"
    has_margins: bool = True
    pen_color: str = "blue_ballpoint"
    font_preset: str = "marck_script"
    jitter: float = 1.0
    slant: float = 1.0
    humanize: bool = True
    custom_gemini_key: Optional[str] = None

@router.get("/presets")
async def get_presets():
    return {
        "presets": [
            {"id": "marck_script", "name": "Курсивный студенческий", "desc": "Живой беглый русский рукописный почерк"},
            {"id": "bad_script", "name": "Небрежный конспект", "desc": "Свободный студенческий почерк шариковой ручкой"},
            {"id": "caveat", "name": "Полупечатный аккуратный", "desc": "Четкий разборчивый почерк для конспектов"},
            {"id": "segoe_print", "name": "Печатный конспект", "desc": "Прямые четкие буквы с легким наклоном"}
        ],
        "paper_styles": [
            {"id": "squared_5mm", "name": "Клетка 5 мм (Школьная/Студенческая)"},
            {"id": "ruled", "name": "Линейка"},
            {"id": "blank", "name": "Белый лист"}
        ],
        "pen_colors": [
            {"id": "blue_ballpoint", "name": "Синяя шариковая", "hex": "#1e40af"},
            {"id": "gel_black", "name": "Черная гелевая", "hex": "#18181b"},
            {"id": "purple", "name": "Фиолетовая чернильная", "hex": "#6b21a8"},
            {"id": "red_ink", "name": "Красная ручка", "hex": "#dc2626"}
        ]
    }

@router.post("/preview")
async def preview_page(req: PreviewRequest):
    """Generates an instant base64 preview of Page 1 for the TMA canvas."""
    try:
        sample_text = req.text if req.text.strip() else (
            "Тема: Пример конспекта\n\n"
            "1. Введение в тему\n"
            "- Рукописный синтез с естественными неровностями строк.\n"
            "[ВАЖНО] Качественная имитация тетрадного листа с полями.\n"
            "[ФОРМУЛА] E = m * c^2\n"
            "- Поддержка умного конспектирования через нейросеть Gemini."
        )

        pages = handwriting_engine.render_conspectus(
            text=sample_text,
            paper_style=req.paper_style,
            has_margins=req.has_margins,
            pen_color=req.pen_color,
            font_preset=req.font_preset,
            jitter=req.jitter,
            slant=req.slant,
            humanize=req.humanize
        )

        preview_img = pages[0]
        buf = BytesIO()
        preview_img.convert("RGB").save(buf, format="JPEG", quality=80)
        b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

        return {
            "page_preview_base64": f"data:image/jpeg;base64,{b64_str}",
            "total_pages": len(pages)
        }
    except Exception as e:
        logger.error("Preview error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_and_deliver(req: GenerateRequest):
    """
    Synthesizes the complete conspectus, builds the PDF, 
    delivers it directly to the user's Telegram chat, and stores records in Supabase.
    """
    try:
        # 1. Format/summarize text via Gemini
        formatted_text = await gemini_service.generate_conspectus_text(
            raw_text=req.text,
            mode=req.mode,
            custom_key=req.custom_gemini_key
        )

        # 2. Render handwritten pages
        pages = handwriting_engine.render_conspectus(
            text=formatted_text,
            paper_style=req.paper_style,
            has_margins=req.has_margins,
            pen_color=req.pen_color,
            font_preset=req.font_preset,
            jitter=req.jitter,
            slant=req.slant,
            humanize=req.humanize
        )

        # 3. Build PDF
        pdf_bytes = pdf_builder.build_pdf_from_images(pages)

        # 4. First page preview JPEG
        pbuf = BytesIO()
        pages[0].convert("RGB").save(pbuf, format="JPEG", quality=85)
        preview_bytes = pbuf.getvalue()

        # Extract title for doc
        title = "Конспект"
        for line in formatted_text.splitlines():
            if line.startswith("Тема:"):
                title = line.replace("Тема:", "").strip()
                break

        # 5. Deliver to user's Telegram chat
        delivery_ok = await delivery_service.send_conspectus_pdf(
            chat_id=req.user_id,
            pdf_bytes=pdf_bytes,
            title=title,
            preview_bytes=preview_bytes
        )

        # 6. Upload to Supabase storage asynchronously
        pdf_url = await supabase_service.upload_asset(
            file_bytes=pdf_bytes,
            remote_filename=f"users/{req.user_id}/conspectus_{title[:20]}.pdf",
            content_type="application/pdf"
        )

        # Log in DB
        await supabase_service.log_conspectus(
            user_id=req.user_id,
            title=title,
            mode=req.mode,
            page_count=len(pages),
            pdf_url=pdf_url
        )

        return {
            "success": True,
            "title": title,
            "page_count": len(pages),
            "delivered_to_chat": delivery_ok,
            "pdf_url": pdf_url
        }

    except Exception as e:
        logger.error("Generation error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calibration-template")
async def get_calibration_template():
    """Returns downloadable printable calibration sheet image."""
    img = sheet_detector.generate_calibration_template_image()
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png", headers={
        "Content-Disposition": "attachment; filename=calibration_template.png"
    })

@router.post("/calibrate")
async def process_calibration_upload(
    user_id: int = Form(...),
    photo: UploadFile = File(...)
):
    """Processes uploaded calibration sheet photo, extracts glyphs and saves to Supabase."""
    try:
        contents = await photo.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # 1. Warp perspective
        warped = sheet_detector.warp_sheet(img_bgr)

        # 2. Extract glyphs from plain A4 (Uppercase, Lowercase, Digits)
        res = glyph_extractor.extract_from_freeform_a4(warped)

        # 3. Save to Supabase
        font_id = await supabase_service.save_user_font(
            user_id=user_id,
            font_name="Мой личный почерк",
            glyph_data=res,
            storage_path=f"users/{user_id}/font.json"
        )

        return {
            "success": True,
            "font_id": font_id,
            "extracted_count": res["extracted_count"],
            "total_chars": res["total_chars"],
            "message": f"Успешно извлечено {res['extracted_count']} из {res['total_chars']} символов вашего почерка!"
        }
    except Exception as e:
        logger.error("Calibration error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
