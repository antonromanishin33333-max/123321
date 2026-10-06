from aiohttp import web
import json

# Разрешаем CORS-запросы (чтобы GitHub Pages мог стучаться на Render)
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

async def handle_options(request):
    return web.Response(status=200, headers=CORS_HEADERS)

async def get_bookings(request):
    user_id = request.query.get("user_id")
    # Достаньте список броней пользователя из вашей базы данных SQLite
    # Пример формата ответа:
    bookings = [
        # {"title": "Зал №1", "datetime": "2026-10-06 18:00", "note": "Предоплата"}
    ]
    return web.json_response(bookings, headers=CORS_HEADERS)

async def add_booking(request):
    data = await request.json()
    # Сохраните data в БД SQLite (user_id, title, datetime, note)
    return web.json_response({"status": "ok"}, headers=CORS_HEADERS)

# В настройках app.router:
# app.router.add_options("/{tail:.*}", handle_options)
# app.router.add_get("/api/bookings", get_bookings)
# app.router.add_post("/api/bookings", add_booking)