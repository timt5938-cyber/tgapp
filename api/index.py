import sys
import os
import traceback
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent

for p in [str(CURRENT_DIR), str(ROOT_DIR), str(CURRENT_DIR / "backend")]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    try:
        from backend.app.main import app
    except ImportError:
        try:
            from api.backend.app.main import app
        except ImportError:
            from app.main import app
except Exception as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger("api.index")
    err_tb = traceback.format_exc()
    logger.error("Failed to import backend app:\n%s", err_tb)

    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI(title="Error Diagnostic")

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def fallback_error_handler(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to initialize backend application",
                "message": str(e),
                "traceback": err_tb.splitlines(),
                "sys_path": sys.path,
                "current_dir": str(CURRENT_DIR),
                "root_dir": str(ROOT_DIR),
                "files_in_root": os.listdir(str(ROOT_DIR)) if ROOT_DIR.exists() else [],
                "files_in_current": os.listdir(str(CURRENT_DIR)) if CURRENT_DIR.exists() else []
            }
        )
