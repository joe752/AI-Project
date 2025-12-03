# Project Designer – GAE API Architecture

## 1. Tech Stack

- **Platform**: Google App Engine Standard
- **Language**: Python 3.10 (or latest supported Python 3.x)
- **Web framework**: FastAPI (preferred) or Flask
  - FastAPI is preferred for:
    - built-in JSON handling
    - request/response models (pydantic)
    - automatic OpenAPI docs

- **HTTP Client**: `httpx` or `requests` to talk to Rube

No database, no message queue.

---

## 2. High-Level Component Diagram

**Clients** (Project Designer Agent / Joey)  
⬇  
**GAE API service** (`AI-Project` repo)  
⬇  
**Rube HTTP API**  
⬇  
**GitHub**

Flow:

1. Client calls the GAE API (e.g., `/api/repo-snapshot`).
2. GAE uses `RUBE_BASE_URL` to call Rube (e.g., `/repos/{project_id}/snapshot`).
3. Rube talks to GitHub and returns raw data.
4. GAE normalizes the response into a clean JSON schema.
5. Client receives normalized JSON.

---

## 3. Directory Structure

Target repo layout (top-level):

```text
AI-Project/
  app.yaml
  requirements.txt

  design/
    spec.md
    architecture.md

  app/
    __init__.py
    main.py          # FastAPI/Flask app entrypoint
    config.py        # config loading (env vars, settings)
    rube_client.py   # all Rube HTTP calls
    schemas.py       # pydantic models / response schemas
    routers/
      __init__.py
      health.py      # /health endpoint
      repo.py        # /api/repo-snapshot and /api/file
