import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional

from .config import settings
from .api.routes_studio import router as studio_router
from .bot.bot_instance import bot, dp
from .bot.handlers import router as bot_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

bot_task: asyncio.Task = None

dp.include_router(bot_router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_task
    # Check if running in serverless environment (Vercel)
    is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))

    if not is_serverless:
        logger.info("Starting Telegram Bot polling (standalone mode)...")
        bot_task = asyncio.create_task(dp.start_polling(bot))
    else:
        logger.info("Running in Serverless mode (Vercel) - bot will receive updates via Webhook (/api/webhook)")

    yield

    # Shutdown bot gracefully
    logger.info("Stopping Telegram Bot polling...")
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
    await bot.session.close()

app = FastAPI(
    title="Telegram Handwritten Conspectus API",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/api/health")
async def health():
    return {"status": "ok", "mode": "serverless" if os.environ.get("VERCEL") else "standalone"}

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    """Processes incoming Telegram updates via Webhook on Vercel."""
    try:
        data = await request.json()
        await dp.feed_raw_update(bot=bot, update=data)
    except Exception as e:
        logger.error("Error processing Telegram webhook update: %s", e)
    return {"ok": True}

@app.get("/api/setup-webhook")
async def setup_webhook(webhook_url: Optional[str] = None):
    """One-click setup of Telegram webhook to your Vercel deployment URL."""
    target_url = webhook_url or f"{settings.MINI_APP_URL.rstrip('/')}/api/webhook"
    if not target_url.startswith("https://"):
        return {
            "success": False,
            "error": f"Telegram requires HTTPS for webhooks. Current target: {target_url}",
            "tip": "Pass your Vercel URL: /api/setup-webhook?webhook_url=https://<your-project>.vercel.app/api/webhook or set MINI_APP_URL in Vercel environment variables."
        }
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        res = await bot.set_webhook(url=target_url)
        info = await bot.get_webhook_info()
        return {
            "success": res,
            "webhook_url": target_url,
            "webhook_info": {
                "url": info.url,
                "has_custom_certificate": info.has_custom_certificate,
                "pending_update_count": info.pending_update_count,
                "last_error_message": info.last_error_message
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Enable CORS for Telegram WebApp iframe
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(studio_router)

# Mount static files (presets & templates)
app.mount("/static", StaticFiles(directory=str(settings.BASE_DIR / "static")), name="static")

# Mount built frontend if it exists
frontend_dist = settings.ROOT_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    @app.get("/")
    def index():
        return {
            "status": "online",
            "message": "Telegram Conspectus API is running. Start the frontend dev server or build frontend/."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
