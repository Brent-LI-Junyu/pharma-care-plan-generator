# Care Plan Generator

Day 2 MVP for a care plan generation system.

## What This Version Does

- Submits patient and order information from a React form.
- Creates an in-memory order in Django.
- Synchronously calls an OpenAI-compatible LLM API to generate a care plan.
- Supports searching an order by `order_id`.
- Supports downloading the generated care plan as a `.txt` file.

This version intentionally does not include database tables, duplicate detection, async queues, workers, WebSocket, tests, or cloud deployment yet.

## Run With Docker

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Then edit `.env` and set your LLM API settings:

```text
OPENAI_API_KEY=sk-your-real-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

For Xiaomi MiMo Token Plan, keep the same variable names but replace the values:

```text
OPENAI_API_KEY=your-xiaomi-mimo-key
OPENAI_BASE_URL=your-xiaomi-openai-compatible-base-url
OPENAI_MODEL=your-xiaomi-model-name
```

Do not commit `.env` to GitHub. It is ignored by `.gitignore`.

From the project root:

```bash
docker compose up --build
```

Then open:

```text
http://localhost:5173
```

Backend API:

```text
http://localhost:8000
```

## API

### POST /api/orders/

Creates an order and synchronously generates a care plan.

### GET /api/orders/{order_id}/

Gets an order and its care plan generation status.

### GET /api/orders/{order_id}/download/

Downloads the generated care plan as a text file.

## Important Day 2 Limitation

Orders are stored in memory. If the backend restarts, existing orders disappear. This is intentional for Day 2. The database is introduced on Day 3.
