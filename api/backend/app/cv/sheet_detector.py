import cv2
import numpy as np
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from ..config import settings

GRID_ROWS = 8
GRID_COLS = 10

# Russian Cyrillic + digits + symbols order in calibration grid
CHAR_SEQUENCE = [
    # Lowercase (33 chars)
    'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и',
    'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
    'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь',
    'э', 'ю', 'я',
    # Digits (10 chars)
    '0', '1', '2', '3', '4', '5', '6',
    '7', '8', '9',
    # Uppercase (33 chars)
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж',
    'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р',
    'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ',
    'Ы', 'Ь', 'Э', 'Ю', 'Я',
    # Punctuation & symbols (4 chars)
    '.', ',', '!', '?'
]

STANDARD_WIDTH = 1200
STANDARD_HEIGHT = 1600
MARGIN = 60

class SheetDetector:
    @staticmethod
    def generate_calibration_template_image() -> Image.Image:
        """Generates the official printable/viewable Calibration Sheet."""
        img = Image.new("RGB", (STANDARD_WIDTH, STANDARD_HEIGHT), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Draw fiducial corner markers (high-contrast black squares for automatic corner detection)
        marker_size = 40
        corners = [
            (MARGIN, MARGIN),
            (STANDARD_WIDTH - MARGIN - marker_size, MARGIN),
            (MARGIN, STANDARD_HEIGHT - MARGIN - marker_size),
            (STANDARD_WIDTH - MARGIN - marker_size, STANDARD_HEIGHT - MARGIN - marker_size)
        ]
        for cx, cy in corners:
            draw.rectangle([cx, cy, cx + marker_size, cy + marker_size], fill=(0, 0, 0))

        # Header instructions
        title = "КАЛИБРОВОЧНЫЙ ЛИСТ ПОЧЕРКА"
        subtitle = "Напишите каждую букву аккуратно внутри соответствующей ячейки"
        draw.text((STANDARD_WIDTH // 2 - 150, MARGIN + 10), title, fill=(30, 30, 30))
        draw.text((STANDARD_WIDTH // 2 - 200, MARGIN + 35), subtitle, fill=(100, 100, 100))

        # Grid area
        grid_top = MARGIN + 80
        grid_bottom = STANDARD_HEIGHT - MARGIN - 20
        grid_left = MARGIN + 20
        grid_right = STANDARD_WIDTH - MARGIN - 20

        cell_w = (grid_right - grid_left) // GRID_COLS
        cell_h = (grid_bottom - grid_top) // GRID_ROWS

        char_idx = 0
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if char_idx >= len(CHAR_SEQUENCE):
                    break
                
                ch = CHAR_SEQUENCE[char_idx]
                x1 = grid_left + c * cell_w
                y1 = grid_top + r * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h

                # Cell border (light grey)
                draw.rectangle([x1, y1, x2, y2], outline=(200, 200, 210), width=1)
                
                # Baseline guide (very faint dot or dashed line)
                base_y = y1 + int(cell_h * 0.75)
                draw.line([(x1 + 5, base_y), (x2 - 5, base_y)], fill=(230, 230, 235), width=1)

                # Character hint in top-left of cell
                draw.text((x1 + 6, y1 + 4), ch, fill=(170, 170, 180))

                char_idx += 1

        return img

    @staticmethod
    def warp_sheet(image_np: np.ndarray) -> np.ndarray:
        """Detects sheet boundary or fiducial markers and warps perspective to standard rectangle."""
        h, w = image_np.shape[:2]
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find largest 4-point contour
        sheet_contour = None
        max_area = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > (w * h * 0.2): # Sheet must cover at least 20% of photo
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                if len(approx) == 4 and area > max_area:
                    sheet_contour = approx
                    max_area = area

        if sheet_contour is not None:
            # Order points: top-left, top-right, bottom-right, bottom-left
            pts = sheet_contour.reshape(4, 2)
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]

            dst = np.array([
                [0, 0],
                [STANDARD_WIDTH - 1, 0],
                [STANDARD_WIDTH - 1, STANDARD_HEIGHT - 1],
                [0, STANDARD_HEIGHT - 1]
            ], dtype="float32")

            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(image_np, M, (STANDARD_WIDTH, STANDARD_HEIGHT))
            return warped

        # Fallback: simple resize if sheet borders weren't clearly isolated
        return cv2.resize(image_np, (STANDARD_WIDTH, STANDARD_HEIGHT))

sheet_detector = SheetDetector()
