import sys
from pathlib import Path

# Add project root to sys.path so backend imports work smoothly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Top-level export of FastAPI app for Vercel static AST parser
from backend.app.main import app

# Explicit module-level variable
app = app
