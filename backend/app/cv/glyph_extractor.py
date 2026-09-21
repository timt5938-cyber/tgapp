import cv2
import numpy as np
import base64
import logging
from typing import Dict, Any, List, Tuple
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

UPPERCASE_CYRILLIC = [
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И',
    'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т',
    'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь',
    'Э', 'Ю', 'Я'
]

LOWERCASE_CYRILLIC = [
    'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и',
    'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
    'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь',
    'э', 'ю', 'я'
]

DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

class GlyphExtractor:
    @staticmethod
    def extract_from_freeform_a4(img_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Extracts handwritten characters directly from a regular A4 or notebook sheet.
        The user simply writes:
        1. Uppercase Cyrillic (А-Я)
        2. Lowercase Cyrillic (а-я)
        3. Digits (0-9)
        """
        h, w = img_bgr.shape[:2]
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Adaptive thresholding for clean ink strokes
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 31, 12
        )

        # Morphological dilation to find text line regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 4))
        dilated = cv2.dilate(thresh, kernel, iterations=2)

        # Find line contours
        line_contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid_lines = []
        for cnt in line_contours:
            x, y, lw, lh = cv2.boundingRect(cnt)
            if lw > w * 0.15 and lh > 15: # Must be a line of writing
                valid_lines.append((y, x, lw, lh))

        # Sort lines from top to bottom
        valid_lines.sort(key=lambda item: item[0])

        glyphs: Dict[str, Any] = {}
        extracted_count = 0

        # If less than 3 lines found, split vertically into 3 bands
        if len(valid_lines) < 3:
            band_h = h // 3
            bands = [
                (0, band_h, UPPERCASE_CYRILLIC),
                (band_h, band_h * 2, LOWERCASE_CYRILLIC),
                (band_h * 2, h, DIGITS)
            ]
        else:
            # Map lines to uppercase, lowercase, digits
            total_lines = len(valid_lines)
            idx_split1 = max(1, int(total_lines * 0.45))
            idx_split2 = max(idx_split1 + 1, int(total_lines * 0.85))

            upper_box = cv2.boundingRect(np.vstack([
                np.array([[x, y], [x+lw, y+lh]]) for y, x, lw, lh in valid_lines[:idx_split1]
            ]))
            lower_box = cv2.boundingRect(np.vstack([
                np.array([[x, y], [x+lw, y+lh]]) for y, x, lw, lh in valid_lines[idx_split1:idx_split2]
            ]))
            digit_box = cv2.boundingRect(np.vstack([
                np.array([[x, y], [x+lw, y+lh]]) for y, x, lw, lh in valid_lines[idx_split2:]
            ]))

            bands = [
                (upper_box[1], upper_box[1] + upper_box[3], UPPERCASE_CYRILLIC),
                (lower_box[1], lower_box[1] + lower_box[3], LOWERCASE_CYRILLIC),
                (digit_box[1], digit_box[1] + digit_box[3], DIGITS)
            ]

        # Extract characters from each band
        for y_start, y_end, char_list in bands:
            y_start = max(0, y_start - 5)
            y_end = min(h, y_end + 5)
            band_patch = thresh[y_start:y_end, :]

            # Find individual character contours
            char_cnts, _ = cv2.findContours(band_patch, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            char_boxes = []
            for cnt in char_cnts:
                cx, cy, cw, ch = cv2.boundingRect(cnt)
                area = cw * ch
                if 20 < area < (w * h * 0.05) and cw > 6 and ch > 10:
                    char_boxes.append((cx, cy, cw, ch))

            # Sort characters from left to right (and top-to-bottom within wrapped lines)
            # Group into sub-lines within the band
            char_boxes.sort(key=lambda b: (b[1] // 40, b[0]))

            for i, (cx, cy, cw, ch) in enumerate(char_boxes):
                if i >= len(char_list):
                    break
                target_char = char_list[i]
                
                # Crop glyph
                pad = 3
                glyph_crop = band_patch[
                    max(0, cy - pad):min(band_patch.shape[0], cy + ch + pad),
                    max(0, cx - pad):min(band_patch.shape[1], cx + cw + pad)
                ]

                # Convert to PIL and base64 PNG
                glyph_pil = Image.fromarray(glyph_crop)
                buf = BytesIO()
                glyph_pil.save(buf, format="PNG")
                b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

                glyphs[target_char] = {
                    "b64": b64_str,
                    "w": int(cw),
                    "h": int(ch),
                    "baseline_offset": int(ch)
                }
                extracted_count += 1

        total_target = len(UPPERCASE_CYRILLIC) + len(LOWERCASE_CYRILLIC) + len(DIGITS)
        return {
            "total_chars": total_target,
            "extracted_count": extracted_count,
            "glyphs": glyphs
        }

glyph_extractor = GlyphExtractor()
