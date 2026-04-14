#!/bin/bash

# === Absolutt base-sti til prosjektet ===
BASE_DIR="$HOME/Documents/MinCodingLinuxV/Prosjekter/6thSemester/DATA3900Bacheloroppgave/Bachelor-CRAI"

# Sjekk at mappa finnes
if [ ! -d "$BASE_DIR" ]; then
  echo "Fant ikke BASE_DIR: $BASE_DIR"
  exit 1
fi

# Valgfritt: frigjør porter hvis noe henger igjen
# .NET API
fuser -k 5056/tcp 2>/dev/null || true

# Python FastAPI
fuser -k 8001/tcp 2>/dev/null || true

# Frontend Vite
fuser -k 5173/tcp 2>/dev/null || true

# --- .NET backend ---
gnome-terminal \
  --title="DeepLungCTApi (.NET)" \
  -- bash -lc "cd \"$BASE_DIR/backEnd/DeepLungCTApi\" \
  && echo '>>> In $(pwd)' \
  && dotnet run \
  ; echo; echo '(.NET) Avsluttet. Trykk ENTER for å lukke...'; read -r"

# --- Python service ---
gnome-terminal \
  --title="inferenceService (FastAPI)" \
  -- bash -lc "cd \"$BASE_DIR/backEnd/inferenceService\" \
  && echo '>>> In $(pwd)' \
  && source .venv/bin/activate \
  && uvicorn app:app --host 127.0.0.1 --port 8001 --reload \
  ; echo; echo '(Python) Avsluttet. Trykk ENTER for å lukke...'; read -r"

# --- Frontend ---
gnome-terminal \
  --title="frontEnd (Vite)" \
  -- bash -lc "cd \"$BASE_DIR/frontEnd\" \
  && echo '>>> In $(pwd)' \
  && npm run dev \
  ; echo; echo '(Frontend) Avsluttet. Trykk ENTER for å lukke...'; read -r"
  