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

## Frontend console

为方便手动验证接口，在仓库内提供了一个无需构建工具的前端（`frontend/`）。它通过浏览器直接调用 FastAPI：

- 标签管理：查看/创建标签。
- 灵感浏览：按风格、标签筛选，快速创建新灵感。
- 用户与收藏：创建用户、将灵感加入收藏并查看收藏列表。
- 沟通卡片：对任意灵感生成沟通卡片预览。

### 启动方式

1. 在一个终端启动 API（需要已有 `.env` 配置）：
   ```bash
   uvicorn app.main:app --reload
   ```

2. 在另一个终端启动静态服务器并打开浏览器：
   ```bash
   # 从仓库根目录
   cd frontend
   python -m http.server 5173
   ```
   然后访问 http://localhost:5173。若后端端口不同，可在页面右上角修改 API 基础地址。

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

