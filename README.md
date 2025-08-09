# Prosta gra turowa

Minimalna dwuosobowa gra turowa z edytorami: mapy, żetonów i rozstawień. Frontend statyczny, backend Flask (REST), gotowe do wdrożenia na Render.

## Uruchomienie lokalne

1. Utwórz i aktywuj środowisko (opcjonalnie).
2. Zainstaluj zależności: `pip install -r requirements.txt`
3. Start serwera dev: `python -m backend.app`
4. Wejdź na http://localhost:5000

Edytory:
- /map_editor.html – edycja mapy
- /token_editor.html – edycja typów żetonów
- /placement_editor.html – rozstawienie jednostek dla obu graczy

Gra:
- Strona główna. Najpierw rozstaw jednostki, potem dołącz jako Gracz A/B i wykonuj ruchy na zmianę (ruch albo atak).

## Deploy na Render

Repo zawiera `render.yaml`. W panelu Render utwórz nowy Web Service z tego repozytorium. Render użyje:

- build: `pip install -r requirements.txt`
- start: `gunicorn -w 2 -b 0.0.0.0:$PORT backend.app:create_app()`

Po deployu udostępnij publiczny URL (np. https://twoj-serwis.onrender.com) graczom.

## API (skrót)
- GET /api/map; POST /api/map
- GET /api/tokens; POST /api/tokens
- GET /api/placements; POST /api/placements
- POST /api/session/join
- GET /api/game/state
- POST /api/game/move
- POST /api/game/reset
