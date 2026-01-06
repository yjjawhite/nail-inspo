# nail-inspo

FastAPI backend prototype for the "nail inspiration" consumer app. It follows the MVP in `PLAN.md`: inspiration feed with tags, favorites, comparison-ready outputs, and communication card generation.

## Getting started

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment variables**

   Create a `.env` file (see `.env.example` for reference) and set `DATABASE_URL` to your Postgres instance. SQLite is the default for local quick starts.

3. **Run the API**
   ```bash
   uvicorn app.main:app --reload
   ```

The OpenAPI docs will be available at `http://localhost:8000/docs`.

## Features

- Inspiration catalog with optional tag/style filters.
- Tag management to seed the taxonomy from the product plan.
- Favorites tied to users for collection and compare flows.
- Communication card generation that pre-fills structure and risk notes for salons.

## Project layout

- `app/config.py` – environment-driven settings.
- `app/database.py` – SQLAlchemy engine/session factory.
- `app/models.py` – core domain models (inspirations, tags, users, favorites, communication cards).
- `app/schemas.py` – Pydantic request/response schemas.
- `app/main.py` – FastAPI app and HTTP routes.

## Seeding sample data

You can quickly seed a few inspirations and tags using the API:

```bash
# Create tags
curl -X POST http://localhost:8000/tags -H "Content-Type: application/json" -d '{"name": "日系", "category": "风格"}'
curl -X POST http://localhost:8000/tags -H "Content-Type: application/json" -d '{"name": "渐变", "category": "元素"}'

# Create an inspiration and attach tags
curl -X POST http://localhost:8000/inspirations -H "Content-Type: application/json" \
  -d '{
    "title": "裸粉渐变猫眼",
    "description": "通勤友好且显白的裸粉渐变",
    "image_url": "https://example.com/nude-gradient.jpg",
    "style": "日系",
    "color_palette": "裸粉",
    "nail_shape": "方圆",
    "length": "短甲友好",
    "duration_estimate_minutes": 75,
    "tags": ["日系", "渐变"]
  }'
```

