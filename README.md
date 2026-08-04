# docx-to-pdf Converter

A FastAPI microservice that converts `.docx` files to PDF using LibreOffice. Designed to run as a Docker container.

## Features

- `POST /convert` — Upload a `.docx` file and receive a PDF in response
- `GET /health` — Health check endpoint
- API key authentication via `x-api-key` header
- Host allowlist enforcement
- Configurable file size limit (default 25 MB)
- Hot-reload development mode
- Production-ready Docker setup with multi-worker Uvicorn

## Requirements

- Docker & Docker Compose

For local (non-Docker) development:

- Python 3.14+
- LibreOffice installed and `soffice` available on `PATH`

## Getting Started

### Development

1. Create an `.env.development` file:

```env
ENVIRONMENT=development
CONVERT_API_KEY=your-dev-key
ALLOWED_HOSTS=localhost
CORS_ORIGINS=http://localhost:3000
```

2. Start the service with hot-reload:

```bash
docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up --build
```

The API will be available at `http://localhost:8000`.  
Interactive docs (Swagger UI) are available at `http://localhost:8000/docs`.

### Production

1. Create an `.env.production` file:

```env
ENVIRONMENT=production
CONVERT_API_KEY=your-secret-key
ALLOWED_HOSTS=your.domain.com
CORS_ORIGINS=https://your.domain.com
```

2. Start the service:

```bash
docker compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d --build
```

## API

### `POST /convert`

Converts a `.docx` file to PDF.

**Headers**

| Header      | Required | Description      |
| ----------- | -------- | ---------------- |
| `x-api-key` | Yes      | API key for auth |

**Body**

`multipart/form-data` with a `file` field containing the `.docx` file.

**Response**

`application/pdf` — the converted PDF file.

**Error codes**

| Code | Reason                                |
| ---- | ------------------------------------- |
| 400  | File is not a `.docx`                 |
| 401  | Missing or invalid API key            |
| 403  | Request host not in allowlist         |
| 413  | File exceeds the 25 MB size limit     |
| 504  | LibreOffice conversion timed out      |
| 500  | Conversion failed or misconfiguration |

**Example**

```bash
curl -X POST http://localhost:8000/convert \
  -H "x-api-key: your-dev-key" \
  -F "file=@document.docx" \
  --output document.pdf
```

### `GET /health`

Returns `{"status": "ok"}` when the service is running.

## Configuration

All configuration is done via environment variables.

| Variable          | Default      | Description                                     |
| ----------------- | ------------ | ----------------------------------------------- |
| `ENVIRONMENT`     | `production` | Set to `development` to enable Swagger/ReDoc UI |
| `CONVERT_API_KEY` | —            | Required. API key for the `/convert` endpoint   |
| `ALLOWED_HOSTS`   | _(all)_      | Comma-separated list of permitted request hosts |
| `CORS_ORIGINS`    | _(none)_     | Comma-separated list of allowed CORS origins    |

## Project Structure

```
app/
├── main.py            # FastAPI app factory, middleware
├── config.py          # Settings from environment variables
├── dependencies.py    # API key and host verification
├── routers/
│   ├── convert.py     # POST /convert endpoint
│   └── health.py      # GET /health endpoint
├── services/
│   └── converter.py   # LibreOffice subprocess wrapper
└── utils/
    └── cleanup.py     # Temp file cleanup utilities
```
