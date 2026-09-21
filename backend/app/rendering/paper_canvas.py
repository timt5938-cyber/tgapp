from PIL import Image, ImageDraw
import numpy as np
from typing import Tuple

PAGE_WIDTH = 1400
PAGE_HEIGHT = 1980

# Color palette for notebook paper
PAPER_BG = (252, 252, 250)         # Warm off-white paper
GRID_COLOR = (210, 222, 238)       # Authentic light blue-grey 5mm grid
LINE_COLOR = (215, 225, 240)       # Ruled horizontal line
MARGIN_COLOR = (225, 75, 75, 200)  # Classic red student margin

class PaperCanvas:
    @staticmethod
    def create_page(
        style: str = "squared_5mm",
        has_margins: bool = True,
        margin_left_px: int = 190,
        margin_right_px: int = 70,
        line_spacing_px: int = 35 # ~5mm in this resolution
    ) -> Image.Image:
        """
        Creates a high-resolution authentic student notebook page.
        """
        img = Image.new("RGBA", (PAGE_WIDTH, PAGE_HEIGHT), PAPER_BG + (255,))
        draw = ImageDraw.Draw(img)

        # 1. Subtle paper noise / gradient
        # Add micro-grain for tactile realism
        np_noise = np.random.normal(0, 1.5, (PAGE_HEIGHT, PAGE_WIDTH)).astype(np.int16)
        base_arr = np.array(img.convert("RGB"), dtype=np.int16)
        noisy_arr = np.clip(base_arr + np_noise[:, :, None], 0, 255).astype(np.uint8)
        img = Image.fromarray(noisy_arr).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # 2. Draw grid or ruled lines
        top_offset = 60
        bottom_offset = PAGE_HEIGHT - 60

        if style == "squared_5mm":
            # Horizontal lines
            for y in range(top_offset, bottom_offset, line_spacing_px):
                draw.line([(0, y), (PAGE_WIDTH, y)], fill=GRID_COLOR, width=1)
            # Vertical lines
            for x in range(30, PAGE_WIDTH - 30, line_spacing_px):
                draw.line([(x, top_offset), (x, bottom_offset)], fill=GRID_COLOR, width=1)

        elif style == "ruled":
            for y in range(top_offset, bottom_offset, line_spacing_px):
                draw.line([(0, y), (PAGE_WIDTH, y)], fill=LINE_COLOR, width=1)

        # 3. Draw vertical red margin rule
        if has_margins:
            # Vertical red margin on left side
            draw.line(
                [(margin_left_px, 0), (margin_left_px, PAGE_HEIGHT)],
                fill=MARGIN_COLOR,
                width=2
            )
            # Subtle margin on the right side if needed
            if margin_right_px > 0:
                draw.line(
                    [(PAGE_WIDTH - margin_right_px, 0), (PAGE_WIDTH - margin_right_px, PAGE_HEIGHT)],
                    fill=(235, 120, 120, 120),
                    width=1
                )

        return img

paper_canvas = PaperCanvas()
