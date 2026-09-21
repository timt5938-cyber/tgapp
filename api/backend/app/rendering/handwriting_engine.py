import os
import random
import math
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from ..config import settings
from .paper_canvas import paper_canvas, PAGE_WIDTH, PAGE_HEIGHT

# Color definitions
PEN_COLORS = {
    "blue_ballpoint": (26, 68, 160, 240),   # Classic blue ballpoint
    "gel_black": (24, 24, 28, 250),        # Deep gel black
    "purple": (78, 30, 140, 240),           # Violet / purple student ink
    "red_ink": (185, 28, 28, 240)           # Red pen
}

# Highlighter colors (semi-transparent)
HIGHLIGHT_YELLOW = (254, 240, 138, 110)
HIGHLIGHT_GREEN = (187, 247, 208, 110)
HIGHLIGHT_ORANGE = (254, 215, 170, 110)

class HandwritingEngine:
    def __init__(self):
        self.presets = {
            "marck_script": settings.PRESETS_DIR / "marck_script.ttf",
            "bad_script": settings.PRESETS_DIR / "bad_script.ttf",
            "caveat": settings.PRESETS_DIR / "caveat.ttf",
            "segoe_print": settings.PRESETS_DIR / "segoe_print.ttf"
        }

    def _get_font(self, preset_name: str, size: int) -> ImageFont.FreeTypeFont:
        font_path = self.presets.get(preset_name)
        if font_path and font_path.exists():
            return ImageFont.truetype(str(font_path), size)
        
        # Fallback to any existing preset or Windows font
        for p in self.presets.values():
            if p.exists():
                return ImageFont.truetype(str(p), size)
        
        return ImageFont.load_default()

    def render_conspectus(
        self,
        text: str,
        paper_style: str = "squared_5mm",
        has_margins: bool = True,
        pen_color: str = "blue_ballpoint",
        font_preset: str = "marck_script",
        jitter: float = 1.0,
        slant: float = 1.0,
        humanize: bool = True
    ) -> List[Image.Image]:
        """
        Renders structured conspectus text across one or more authentic notebook pages.
        Returns a list of PIL Images (one per page).
        """
        primary_color = PEN_COLORS.get(pen_color, PEN_COLORS["blue_ballpoint"])
        
        # Font sizes matched to 35px 5mm grid cells
        font_main = self._get_font(font_preset, 24)
        font_title = self._get_font(font_preset, 30)
        font_small = self._get_font(font_preset, 20)

        # Margins layout
        margin_left = 220 if has_margins else 100
        margin_right = PAGE_WIDTH - 80
        content_width = margin_right - margin_left

        line_spacing = 35 # Grid cell height
        start_y = 100
        max_y = PAGE_HEIGHT - 100

        pages: List[Image.Image] = []
        current_page = paper_canvas.create_page(style=paper_style, has_margins=has_margins)
        draw = ImageDraw.Draw(current_page)
        curr_y = start_y

        # Word wrap helper
        raw_lines = text.splitlines()
        wrapped_lines: List[Tuple[str, str]] = [] # (line_text, line_type)

        for raw in raw_lines:
            line_str = raw.strip()
            if not line_str:
                wrapped_lines.append(("", "empty"))
                continue

            line_type = "normal"
            if line_str.startswith("Тема:") or line_str.startswith("# "):
                line_type = "title"
                line_str = line_str.replace("# ", "").strip()
            elif line_str.startswith("[ВАЖНО]") or line_str.startswith("[ОПР]") or line_str.startswith("[ВЫВОД]"):
                line_type = "highlight"
            elif line_str.startswith("[ФОРМУЛА]"):
                line_type = "formula"
                line_str = line_str.replace("[ФОРМУЛА]", "").strip()
            elif line_str.startswith("- ") or line_str.startswith("• "):
                line_type = "bullet"

            # Word wrap within content_width
            words = line_str.split(" ")
            current_chunk = []
            f = font_title if line_type == "title" else font_main

            for word in words:
                test_str = " ".join(current_chunk + [word])
                bbox = draw.textbbox((0, 0), test_str, font=f)
                w = bbox[2] - bbox[0]
                if w > content_width and current_chunk:
                    wrapped_lines.append((" ".join(current_chunk), line_type))
                    current_chunk = [word]
                else:
                    current_chunk.append(word)

            if current_chunk:
                wrapped_lines.append((" ".join(current_chunk), line_type))

        # Render lines onto pages
        for line_str, ltype in wrapped_lines:
            if curr_y + line_spacing > max_y:
                # Page full, create new page
                pages.append(current_page)
                current_page = paper_canvas.create_page(style=paper_style, has_margins=has_margins)
                draw = ImageDraw.Draw(current_page)
                curr_y = start_y

            if ltype == "empty":
                curr_y += line_spacing // 2
                continue

            # Calculate natural jitter
            y_jitter = random.uniform(-1.5, 1.5) * jitter
            x_jitter = random.uniform(-1.0, 1.5) * jitter
            actual_x = margin_left + x_jitter
            actual_y = curr_y + y_jitter

            if ltype == "bullet":
                actual_x += 25

            # Humanization: Highlighting
            if ltype == "highlight" and humanize:
                tag_end = line_str.find("]")
                tag = line_str[:tag_end+1] if tag_end != -1 else ""
                body = line_str[tag_end+1:].strip() if tag_end != -1 else line_str
                
                # Draw marker stroke behind text
                bbox = draw.textbbox((actual_x, actual_y), line_str, font=font_main)
                pad_h = 4
                highlight_box = [bbox[0] - 6, bbox[1] - pad_h, bbox[2] + 8, bbox[3] + pad_h]
                draw.rounded_rectangle(highlight_box, radius=4, fill=HIGHLIGHT_YELLOW)
                
                # Draw text
                draw.text((actual_x, actual_y), line_str, font=font_main, fill=primary_color)

            elif ltype == "formula" and humanize:
                # Center formula and draw hand-drawn box around it
                bbox = draw.textbbox((0, 0), line_str, font=font_main)
                fw = bbox[2] - bbox[0]
                formula_x = margin_left + (content_width - fw) // 2
                draw.text((formula_x, actual_y), line_str, font=font_main, fill=(20, 20, 60, 255))
                
                # Hand-drawn rectangular border with slight waviness
                f_bbox = [formula_x - 15, actual_y - 6, formula_x + fw + 15, actual_y + line_spacing - 4]
                draw.rectangle(f_bbox, outline=primary_color, width=1)

            elif ltype == "title":
                draw.text((actual_x, actual_y), line_str, font=font_title, fill=primary_color)
                # Hand-drawn double underline under the title
                t_bbox = draw.textbbox((actual_x, actual_y), line_str, font=font_title)
                line_y1 = t_bbox[3] + 4 + random.uniform(-1, 1)
                line_y2 = line_y1 + 4
                draw.line([(actual_x, line_y1), (t_bbox[2], line_y1)], fill=primary_color, width=1)
                curr_y += 10

            else:
                # Normal student line
                # Simulate occasional slight ink density fluctuation
                draw.text((actual_x, actual_y), line_str, font=font_main, fill=primary_color)

            curr_y += line_spacing

        # Append final page
        pages.append(current_page)
        return pages

handwriting_engine = HandwritingEngine()
