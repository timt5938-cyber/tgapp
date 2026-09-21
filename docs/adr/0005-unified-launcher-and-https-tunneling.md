# 5. Unified Launcher and HTTPS Tunneling

To provide seamless local development and production readiness, the application will feature both Docker Compose orchestration and a cross-platform Python launcher (`run.py`) equipped with automated HTTPS tunneling (via Cloudflare Tunnel / ngrok) for Telegram Mini App testing.

## Considered Options
- **Manual multi-terminal execution:** Requires starting the FastAPI backend, Vite dev server, and tunnel independently across multiple windows. High friction for local testing.
- **Docker-only production setup:** Clean for servers, but slower reload times for local frontend iterating.
- **Unified Launcher with Auto-tunneling (Selected):** `run.py` starts both backend and frontend concurrently, automatically provisions a secure temporary HTTPS tunnel for Telegram WebApp verification, and updates configuration dynamically. `docker-compose.yml` is provided for containerized server deployments.

## Consequences
- Requires no external tunneling accounts for basic testing (Cloudflare quick tunnels do not require an account or credit card).
- Frontend static assets can be built and served directly by FastAPI in unified mode, or served hot via Vite in development mode.
