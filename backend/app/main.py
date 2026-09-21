import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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
    # Start bot polling in background
    logger.info("Starting Telegram Bot polling...")
    bot_task = asyncio.create_task(dp.start_polling(bot))

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
