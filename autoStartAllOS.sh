#!/bin/bash
# autoStartAllOS.sh — Linux & macOS
# Run from anywhere; paths are resolved relative to this script's location.

# ── Resolve project root ───────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$SCRIPT_DIR"

# ── Free ports ─────────────────────────────────────────────────────────────────
free_port() {
    local port="$1"
    if command -v fuser &>/dev/null; then
        fuser -k "${port}/tcp" 2>/dev/null || true
    elif command -v lsof &>/dev/null; then
        lsof -ti tcp:"$port" | xargs kill -9 2>/dev/null || true
    fi
}

echo "Freeing ports 5056, 8001, 5173..."
free_port 5056
free_port 8001
free_port 5173

# ── Open a new terminal window ─────────────────────────────────────────────────
OS="$(uname -s)"

open_term() {
    local title="$1"
    local cmd="$2"
    local full_cmd="$cmd; echo; echo 'Press ENTER to close...'; read -r"

    case "$OS" in
        Linux)
            if command -v gnome-terminal &>/dev/null; then
                gnome-terminal --title="$title" -- bash -lc "$full_cmd"
            elif command -v konsole &>/dev/null; then
                konsole --title "$title" -e bash -lc "$full_cmd" &
            elif command -v xterm &>/dev/null; then
                xterm -title "$title" -e bash -lc "$full_cmd" &
            else
                echo "No terminal emulator found for: $title — running in background."
                bash -lc "$cmd" &
            fi
            ;;
        Darwin)
            osascript \
                -e "tell application \"Terminal\"" \
                -e "  activate" \
                -e "  do script \"$cmd\"" \
                -e "end tell"
            ;;
        *)
            echo "Unsupported OS: $OS"
            exit 1
            ;;
    esac
}

# ── Services ───────────────────────────────────────────────────────────────────

# .NET backend
open_term "DeepLungCTApi (.NET)" \
    "cd '$BASE_DIR/backEnd/DeepLungCTApi' && echo '>>> In \$(pwd)' && dotnet run"

# Python inference service
open_term "inferenceService (FastAPI)" \
    "cd '$BASE_DIR/backEnd/inferenceService' && echo '>>> In \$(pwd)' && source .venv/bin/activate && uvicorn app:app --host 127.0.0.1 --port 8001 --reload"

# React frontend
open_term "frontEnd (Vite)" \
    "cd '$BASE_DIR/frontEnd' && echo '>>> In \$(pwd)' && npm run dev"

echo "All services started!"
