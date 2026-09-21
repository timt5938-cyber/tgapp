import logging
from io import BytesIO
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, 
    WebAppInfo, BufferedInputFile
)
from ..config import settings
from ..storage.supabase_client import supabase_service
from ..gemini.client import gemini_service
from ..rendering.handwriting_engine import handwriting_engine
from ..rendering.pdf_builder import pdf_builder
from ..cv.sheet_detector import sheet_detector
from .delivery import delivery_service
from .bot_instance import bot

logger = logging.getLogger(__name__)
router = Router()

def get_main_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    
    app_url = settings.MINI_APP_URL
    if app_url and app_url.startswith("https://"):
        buttons.append([
            InlineKeyboardButton(
                text="✍️ Открыть Студию Конспектов",
                web_app=WebAppInfo(url=app_url)
            )
        ])
    elif app_url and "localhost" in app_url:
        buttons.append([
            InlineKeyboardButton(
                text="💻 Веб-студия (localhost:8000)",
                callback_data="howto_localhost"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="📷 Как добавить свой почерк (А4)",
            callback_data="howto_calibrate"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    if user:
        await supabase_service.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )

    welcome_text = (
        f"👋 Привет, <b>{user.first_name if user else 'друг'}</b>!\n\n"
        f"Я создаю <b>реалистичные рукописные конспекты</b> прямо в тетрадях в клетку или линейку с полями.\n\n"
        f"✨ <b>Как пользоваться:</b>\n"
        f"1. <b>Веб-студия</b> — откройте <a href=\"http://localhost:8000\">http://localhost:8000</a> в браузере (живое превью, выбор тетради, пасты, печать в PDF).\n"
        f"2. <b>Голосовые и аудио</b> — отправьте голосовое прямо сюда в чат, и я сгенерирую готовый конспект в PDF!\n"
        f"3. <b>Фото страниц/лекций</b> — пришлите фото, и я превращу материал в рукописный конспект.\n"
        f"4. <b>Свой почерк</b> — напишите на обычном листе А4 заглавные (А-Я), строчные (а-я) буквы и цифры (0-9), и отправьте мне фото с подписью <code>почерк</code>!"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "📖 <b>Инструкция по использованию:</b>\n\n"
        "• <b>Веб-студия:</b> Откройте <a href=\"http://localhost:8000\">http://localhost:8000</a> в браузере.\n"
        "• <b>Быстрый конспект из чата:</b> Отправьте текст, аудиозапись лекции или фото слайдов.\n"
        "• <b>Свой почерк:</b> Напишите от руки на обычном листе А4 буквы и цифры, сфотографируйте и отправьте фото в чат с подписью <code>почерк</code>.\n"
        "• <b>Готовый результат:</b> Готовый многостраничный PDF-файл конспекта придёт прямо в этот чат!"
    )
    await message.answer(help_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "howto_localhost")
async def callback_howto_localhost(callback: CallbackQuery):
    await callback.answer()
    msg = (
        "💻 <b>Веб-студия запущена на localhost!</b>\n\n"
        "Откройте ссылку в браузере на вашем компьютере:\n"
        "👉 <a href=\"http://localhost:8000\">http://localhost:8000</a>\n\n"
        "В веб-интерфейсе доступен полный функционал:\n"
        "• Интерактивный живой предпросмотр конспекта (с зумом)\n"
        "• Выбор тетради (клетка 5 мм, линейка, чистый лист) и полей\n"
        "• Цвета чернил (синяя шариковая, гелевая, черная, фиолетовая, карандаш)\n"
        "• Настройка естественного наклона, дрожания руки и выделителей"
    )
    if callback.message:
        await callback.message.answer(msg, parse_mode="HTML")

@router.callback_query(F.data == "howto_calibrate")
async def callback_howto_calibrate(callback: CallbackQuery):
    await callback.answer()
    msg = (
        "✍️ <b>Как добавить свой почерк:</b>\n\n"
        "Никаких шаблонов или бланков распечатывать не нужно!\n\n"
        "1. Возьмите обычный чистый лист бумаги (А4 или тетрадный лист).\n"
        "2. Напишите от руки шариковой или гелевой ручкой:\n"
        "   • <b>1. Заглавные буквы:</b> А Б В Г Д Е Ё Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я\n"
        "   • <b>2. Строчные буквы:</b> а б в г д е ё ж з и й к л м н о п р с т у ф х ц ч ш щ ъ ы ь э ю я\n"
        "   • <b>3. Цифры:</b> 0 1 2 3 4 5 6 7 8 9\n\n"
        "3. Сфотографируйте лист при хорошем освещении и <b>отправьте фото сюда в чат</b> с подписью <code>почерк</code>!\n"
        "Нейросеть и алгоритм CV сегментируют символы и сохранят ваш личный шрифт."
    )
    if callback.message:
        await callback.message.answer(msg, parse_mode="HTML")

@router.message(F.voice | F.audio)
async def handle_audio_message(message: Message):
    status_msg = await message.answer("🎧 <i>Слушаю аудиозапись лекции и составляю конспект через Gemini...</i>")
    try:
        user_id = message.from_user.id if message.from_user else 0
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        file_info = await bot.get_file(file_id)
        
        # Download audio
        audio_stream = BytesIO()
        await bot.download_file(file_info.file_path, audio_stream)
        audio_bytes = audio_stream.getvalue()
        mime = "audio/ogg" if message.voice else "audio/mpeg"

        # Generate conspectus via Gemini
        conspectus_text = await gemini_service.generate_conspectus_text(
            audio_bytes=(audio_bytes, mime),
            mode="smart"
        )

        # Render handwritten pages
        pages = handwriting_engine.render_conspectus(
            text=conspectus_text,
            paper_style="squared_5mm",
            has_margins=True,
            pen_color="blue_ballpoint"
        )

        # Build PDF
        pdf_data = pdf_builder.build_pdf_from_images(pages)

        # Preview photo
        pbuf = BytesIO()
        pages[0].convert("RGB").save(pbuf, format="JPEG", quality=85)
        
        await status_msg.delete()
        await delivery_service.send_conspectus_pdf(
            chat_id=message.chat.id,
            pdf_bytes=pdf_data,
            title="Конспект по аудиозаписи",
            preview_bytes=pbuf.getvalue()
        )
    except Exception as e:
        logger.error("Error processing audio message: %s", e)
        await status_msg.edit_text("❌ Произошла ошибка при обработке аудио. Попробуйте еще раз или используйте Mini App.")

@router.message(F.photo)
async def handle_photo_message(message: Message):
    user_id = message.from_user.id if message.from_user else 0
    caption_text = (message.caption or "").lower()

    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        
        photo_stream = BytesIO()
        await bot.download_file(file_info.file_path, photo_stream)
        img_bytes = photo_stream.getvalue()

        # Check if this photo is a handwriting sample
        if "почерк" in caption_text or "калибровк" in caption_text:
            status_msg = await message.answer("✍️ <i>Считываю ваш почерк с фото...</i>")
            try:
                import numpy as np
                import cv2
                from ..cv.glyph_extractor import glyph_extractor
                from ..cv.sheet_detector import sheet_detector

                nparr = np.frombuffer(img_bytes, np.uint8)
                img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                warped = sheet_detector.warp_sheet(img_bgr)
                res = glyph_extractor.extract_from_freeform_a4(warped)

                await supabase_service.save_user_font(
                    user_id=user_id,
                    font_name="Мой личный почерк",
                    glyph_data=res,
                    storage_path=f"users/{user_id}/font.json"
                )

                await status_msg.edit_text(
                    f"🎉 <b>Ваш почерк успешно сохранен!</b>\n\n"
                    f"Распознано символов: <b>{res['extracted_count']}</b> из {res['total_chars']}.\n"
                    f"Теперь ваши конспекты будут оформляться вашей собственной рукой!"
                )
                return
            except Exception as e:
                logger.error("Error extracting handwriting: %s", e)
                await status_msg.edit_text("❌ Не удалось распознать буквы на фото. Убедитесь, что лист освещен ровно, и попробуйте снова.")
                return

        # Normal lecture photo handling
        status_msg = await message.answer("📷 <i>Распознаю материал со снимка и оформляю рукописный конспект...</i>")

        # Process with Gemini
        conspectus_text = await gemini_service.generate_conspectus_text(
            raw_text=caption_text if caption_text else None,
            images_bytes=[(img_bytes, "image/jpeg")],
            mode="smart"
        )

        pages = handwriting_engine.render_conspectus(
            text=conspectus_text,
            paper_style="squared_5mm",
            has_margins=True,
            pen_color="blue_ballpoint"
        )

        pdf_data = pdf_builder.build_pdf_from_images(pages)
        pbuf = BytesIO()
        pages[0].convert("RGB").save(pbuf, format="JPEG", quality=85)

        await status_msg.delete()
        await delivery_service.send_conspectus_pdf(
            chat_id=message.chat.id,
            pdf_bytes=pdf_data,
            title="Конспект по фотоматериалам",
            preview_bytes=pbuf.getvalue()
        )
    except Exception as e:
        logger.error("Error processing photo message: %s", e)
        await status_msg.edit_text("❌ Не удалось обработать фото. Попробуйте отправить в Mini App.")
