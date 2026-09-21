# 3. Python (FastAPI, aiogram 3, OpenCV) and React Mini App Stack

The core system architecture will be split between a Python backend (orchestrating computer vision, PDF generation, LLM transformation, and Telegram bot handling) and a React/Vite/Tailwind frontend for the Telegram Mini App.

## Considered Options
- **Node.js / TypeScript end-to-end:** Unified language across client and server, but lacks mature computer vision libraries comparable to OpenCV for perspective correction and contour extraction.
- **Monolithic Python with Jinja2 / Vanilla JS:** Simpler deployment without a separate frontend build, but clumsy for reactive client-side canvas zoom, multi-page flip preview, and modern mobile Telegram UX.
- **Python Backend + React Frontend (Selected):** Leverages OpenCV/Pillow for precise glyph extraction and document synthesis, aiogram 3 for Telegram Bot operations, and React + Tailwind for a high-fidelity mobile Mini App experience.

## Consequences
- Requires a two-tier repository structure: `backend/` (FastAPI, OpenCV, aiogram) and `frontend/` (React, Vite, Telegram WebApp SDK).
- Development environment requires Python 3.10+ and Node.js.
