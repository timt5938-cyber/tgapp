# Conspectus Handwriting Bot

A Telegram Mini App system that turns raw text, topics, or voice into realistic handwritten lecture notes on notebook paper, mimicking handwriting.

## Language

**Handwriting Synthesis**:
Rendering digital text onto virtual notebook/ruled paper to visually resemble human handwriting, including natural variations, slant, and ink flow.
_Avoid_: Font printing, plain OCR

**Handwriting Sample**:
Photos or scans provided by the user demonstrating their writing style.
_Avoid_: Dataset, training dump

**Calibration Sheet**:
A standardized printable or drawn grid containing alphabet letters, numbers, and symbols that the user fills out to capture their individual handwriting.
_Avoid_: Random note, freeform scan

**Glyph Extraction**:
The computer vision process of isolating, cleaning, and vectorizing individual handwritten characters from a calibration sheet.
_Avoid_: Character recognition, OCR text dump

**Preset Font**:
A built-in curated handwriting style (e.g., Neat Student, Swift Cursive, Semi-print) available immediately without prior user calibration.
_Avoid_: Stock font, system font

**Personal Font**:
A custom font or glyph library synthesized directly from the user's uploaded Calibration Sheet to mimic their authentic writing.
_Avoid_: User profile, clone font

**Raw Input**:
The source materials submitted by the user, such as text, audio, or slide images.
_Avoid_: Prompt, message payload

**Synthesis Mode**:
The processing strategy chosen by the user: either *Smart Conspectus* (LLM extraction and summarization) or *Verbatim* (word-for-word replication).
_Avoid_: Prompt style, output flag

**Notebook Style**:
The visual background configuration for rendered pages, including ruled lines, grid cells, red margins, and paper textures.
_Avoid_: Theme, template canvas

**Paper Grid**:
A mathematically generated or textured 5mm squared (клетка) or ruled (линейка) canvas with authentic school/university margin lines.
_Avoid_: Graph paper image, background wallpaper

**Ink Style**:
The rendering characteristics of the pen stroke, including color palette (blue ballpoint, gel black, red), line width variation, and natural jitter.
_Avoid_: Color picker, brush preset

**Humanization Artifacts**:
Procedural imperfections injected into the rendering pipeline (baseline jitter, ink flow variations, slant variation, intentional strikethroughs, marker highlighting) to prevent synthetic appearance.
_Avoid_: Render bugs, random noise

**Cloud Store**:
The managed Supabase cloud database and object storage housing user profiles, custom font glyph bundles, and compiled conspectuses.
_Avoid_: Local dump, hard drive cache

**Conspectus**:
The structured final note (synthesized text and structure) ready to be rendered onto paper.
_Avoid_: Summary dump, raw output
