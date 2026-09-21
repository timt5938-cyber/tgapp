#!/usr/bin/env python3
"""
Telegram Handwritten Conspectus Studio - Unified Launcher
Runs backend, frontend, and optional Cloudflare HTTPS tunnel for Telegram testing.
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"
BACKEND_DIR = ROOT_DIR / "backend"

def print_banner():
    print("=" * 65)
    print("   ✍️  TELEGRAM HANDWRITTEN CONSPECTUS STUDIO & BOT")
    print("=" * 65)
    print("   Бот токен: 8941440413:AAHQob9S6KPZBPaJS3czdkY4pCM3rB68Nmc")
    print("   Supabase:  https://faxtkubhxjesghpduiba.supabase.co")
    print("=" * 65)

def check_frontend_build():
    dist_dir = FRONTEND_DIR / "dist"
    if not dist_dir.exists():
        print("📦 Сборка фронтенда React/Vite...")
        if not (FRONTEND_DIR / "node_modules").exists():
            print("⏳ Установка npm зависимостей...")
            subprocess.run(["npm", "install"], cwd=str(FRONTEND_DIR), shell=True, check=True)
        print("⚙️  Сборка static assets...")
        subprocess.run(["npm", "run", "build"], cwd=str(FRONTEND_DIR), shell=True, check=True)
        print("✅ Фронтенд успешно собран в dist/!")

def start_cloudflare_tunnel(port=8000):
    """Starts a cloudflared quick tunnel if installed."""
    cf_bin = shutil.which("cloudflared")
    if not cf_bin:
        print("\n💡 Для работы Mini App внутри Telegram требуется HTTPS ссылка.")
        print("   Установите cloudflared (winget install Cloudflare.cloudflared)")
        print("   или ngrok (ngrok http 8000)")
        return None

    print("\n🌐 Запуск Cloudflare HTTPS туннеля...")
    tunnel_proc = subprocess.Popen(
        [cf_bin, "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    return tunnel_proc

def main():
    print_banner()

    # Check for --dev flag
    is_dev = "--dev" in sys.argv

    if not is_dev:
        check_frontend_build()

    # Check for --tunnel flag
    tunnel_proc = None
    if "--tunnel" in sys.argv:
        tunnel_proc = start_cloudflare_tunnel(port=8000 if not is_dev else 5173)

    processes = []

    try:
        if is_dev:
            print("\n🚀 Запуск в режиме разработки:")
            print("   1. FastAPI Backend + Bot на http://localhost:8000")
            print("   2. Vite Frontend на http://localhost:5173")
            
            # Start Vite
            vite_proc = subprocess.Popen(["npm", "run", "dev"], cwd=str(FRONTEND_DIR), shell=True)
            processes.append(vite_proc)

            # Start Backend
            uvicorn_cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
            backend_proc = subprocess.Popen(uvicorn_cmd, cwd=str(ROOT_DIR))
            processes.append(backend_proc)

        else:
            print("\n🚀 Запуск сервера и Telegram бота на http://localhost:8000...")
            print("   (Фронтенд Mini App отдаётся напрямую с бэкенда)")
            uvicorn_cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
            backend_proc = subprocess.Popen(uvicorn_cmd, cwd=str(ROOT_DIR))
            processes.append(backend_proc)

        print("\n✨ Приложение запущено! Нажмите Ctrl+C для остановки.")
        
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Остановка процессов...")
        for p in processes:
            p.terminate()
        if tunnel_proc:
            tunnel_proc.terminate()
        print("До свидания!")

if __name__ == "__main__":
    main()
