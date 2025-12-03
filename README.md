# Project Designer - GAE API

A lightweight **Google App Engine (GAE)** HTTP API service that provides repository inspection capabilities via Rube integration.

## Overview

This FastAPI-based service acts as a bridge between:
- **Rube** (GitHub repository inspection service)
- **External clients** (Project Designer Agent, manual inspection tools)

The service is:
- **Stateless** - no database required
- **Low-cost** - scales to zero on GAE Standard
- **Minimal** - focused on core repo inspection features

## Features

- **Health Check** - Service status verification
- **Repository Snapshot** - Get file/folder structure with metadata
- **File Content Retrieval** - Fetch specific file contents on-demand
- **Auto-generated API Docs** - Interactive OpenAPI documentation

## API Endpoints

### `GET /health`
Health check endpoint to verify service is running.

**Response:**
```json
{
  "status": "ok",
  "service": "gae-api"
}
```

### `GET /api/repo-snapshot`
Get repository file structure and metadata.

**Query Parameters:**
- `project_id` (required): Project/repository identifier

**Response:**
```json
{
  "project_id": "example-repo",
  "files": [
    {
      "path": "src/main.py",
      "type": "file",
      "size": 1024,
      "sha": "abc123..."
    }
  ],
  "commit_info": { ... }
}
```

### `GET /api/file`
Get content of a specific file.

**Query Parameters:**
- `project_id` (required): Project/repository identifier
- `path` (required): File path within repository

**Response:**
```json
{
  "project_id": "example-repo",
  "path": "src/main.py",
  "content": "# File contents here...",
  "encoding": "utf-8",
  "size": 1024
}
```

### `GET /`
Root endpoint with service information and links to documentation.

## Setup

### Prerequisites

- Python 3.10 or later
- Google Cloud SDK (for deployment)
- Git

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/joe752/AI-Project.git
   cd AI-Project
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   Create a `.env` file in the root directory:
   ```
   RUBE_BASE_URL=https://your-rube-instance.com
   LOG_LEVEL=INFO
   ```

5. **Run the development server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

6. **Access interactive API documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## Deployment to Google App Engine

### Prerequisites
- Google Cloud project with App Engine enabled
- `gcloud` CLI installed and configured

### Deploy Steps

1. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth login
   ```

2. **Set your project:**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Update `app.yaml` configuration:**

   Edit the `RUBE_BASE_URL` in `app.yaml`:
   ```yaml
   env_variables:
     RUBE_BASE_URL: "https://your-actual-rube-url.com"
   ```

4. **Deploy to App Engine:**
   ```bash
   gcloud app deploy
   ```

5. **View your deployed app:**
   ```bash
   gcloud app browse
   ```

### Deployment Configuration

The `app.yaml` file configures:
- **Runtime**: Python 3.10
- **Instance class**: F1 (minimal cost)
- **Scaling**: 0 to 10 instances (scales to zero when idle)
- **Environment variables**: Configure Rube connection

## Project Structure

```
AI-Project/
├── app.yaml                    # GAE deployment configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
├── design/
│   ├── spec.md                # API specification
│   └── architecture.md        # Architecture documentation
└── app/
    ├── __init__.py
    ├── main.py                # FastAPI application entrypoint
    ├── config.py              # Configuration management
    ├── schemas.py             # Pydantic models
    ├── rube_client.py         # HTTP client for Rube
    └── routers/
        ├── __init__.py
        ├── health.py          # Health check endpoint
        └── repo.py            # Repository endpoints
```

## Configuration

### Environment Variables

- `RUBE_BASE_URL` - Base URL for Rube service (required)
- `LOG_LEVEL` - Logging level (default: INFO)
- `API_KEY` - Optional API key for authentication (future use)

## Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `400` - Bad request (missing/invalid parameters)
- `404` - Resource not found (repo or file)
- `500` - Internal server error
- `502` - Bad gateway (Rube error)
- `503` - Service unavailable (Rube unreachable)

All errors return JSON:
```json
{
  "error": "Human-readable error message"
}
```

## Logging

The service logs:
- Incoming requests (method, path)
- Response status codes
- Errors with details for debugging
- Rube communication attempts

Logs are available in Google Cloud Console under App Engine logs.

## Testing

Run local tests manually by accessing endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Get repo snapshot
curl "http://localhost:8000/api/repo-snapshot?project_id=test-repo"

# Get file content
curl "http://localhost:8000/api/file?project_id=test-repo&path=README.md"
```

## Future Enhancements

Planned features (not in MVP):
- API key authentication
- Project Designer Agent proxy endpoint
- Enhanced commit/branch information
- Diff summaries
- Rate limiting

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues or questions:
- GitHub Issues: https://github.com/joe752/AI-Project/issues
- Documentation: See `design/` folder for detailed specs
