# Care Plan Generator

Day 2 MVP for a care plan generation system.

## What This Version Does

- Submits patient and order information from a React form.
- Creates an in-memory order in Django.
- Synchronously generates a simple care plan.
- Supports searching an order by `order_id`.
- Supports downloading the generated care plan as a `.txt` file.

This version intentionally does not include database tables, duplicate detection, async queues, workers, WebSocket, tests, or cloud deployment yet.

## Run With Docker

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
