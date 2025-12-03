# Project Designer – GAE API Spec

## 1. Overview

This project is a **small Google App Engine (GAE) HTTP API** that sits between:

- **Rube** (which knows how to talk to GitHub and inspect repos), and  
- **external clients** such as:
  - a future **Project Designer Agent** (running in Agent Builder), and
  - Joey manually, when he wants to inspect or debug things.

The service is intentionally:

- **Stateless**
- **Low-cost** (GAE Standard, scales to zero, no database)
- **Minimal in scope**

Its main job is to provide:

1. A **lightweight repo snapshot** (structure only, no file content by default).  
2. **On-demand file content** for specific paths (when explicitly requested).  
3. A basic **health check** endpoint.

Later, this service may also expose a proxy endpoint for talking to a Project Designer Agent or other services, but that is *not* required for the first version.

---

## 2. Goals

1. Provide a **clean, stable JSON API** that any agent or tool can call to:
   - Get a list of files and basic metadata from a repo via Rube.
   - Fetch the contents of a single file when needed.

2. Run on **Google App Engine Standard** with:
   - minimal configuration
   - no database
   - environment-based configuration for Rube

3. Be easy to extend in the future with:
   - more repo-related endpoints
   - optional “designer proxy” endpoints

---

## 3. Non-Goals

- No direct integration with Claude Code or Anthropic APIs from this service.
- No direct GitHub logic here (all repo knowledge comes **only** from Rube).
- No user-facing UI.
- No authentication logic beyond optional simple API key headers if needed later.
- No background workers or cron jobs.

---

## 4. External Dependencies

### 4.1 Rube

Rube is assumed to already exist as an HTTP-accessible service that can:

1. Return a **repo snapshot** (file/folder structure + basic metadata).  
2. Return **file contents** for a specific path.

This GAE service will call Rube via HTTP using a base URL from an environment variable.

Expected env var:

- `RUBE_BASE_URL` – base URL for Rube’s HTTP API, e.g. `https://rube.example.com`

(If Rube is not yet implemented, Claude should still implement the client and keep the base URL configurable.)

### 4.2 Google App Engine

The service should be deployed to **GAE Standard**:

- Python 3.x runtime (e.g., Python 3.10)
- `min_instances: 0` to allow scaling to zero.
- Small instance class (F1) for low cost.

---

## 5. High-Level Features

1. **Health check**

   - Simple endpoint to verify the service is running.

2. **Repo snapshot**

   - Given a `project_id` (or repo name), return:
     - a list of files with paths and basic metadata
     - optional recent commit summaries (if Rube supports that)

3. **File content**

   - Given a `project_id` and `path`, return:
     - the raw text content of the file at that path (UTF-8)

---

## 6. Usage Scenarios

### 6.1 Project Designer Agent sync

1. Project Designer Agent calls `GET /api/repo-snapshot?project_id=...`
2. GAE service calls Rube, transforms the response into its standard JSON shape.
3. Agent updates its internal repo map and design model using the response.

### 6.2 On-demand file review

1. Joey or the Project Designer Agent decides a specific file needs inspection.
2. They call `GET /api/file?project_id=...&path=...`
3. GAE service calls Rube, gets the file content, and returns it as JSON.

---

## 7. Error Handling Requirements

- Use appropriate HTTP status codes:
  - `200` for success
  - `400` for bad/missing parameters
  - `404` if Rube reports “repo not found” or “file not found”
  - `502` or `503` if Rube is unavailable
- Always return a JSON body with:
  - on success: the requested data
  - on error: `{ "error": "<human-readable message>" }`

---

## 8. Logging

- Log incoming requests and responses at a basic level (method, path, status).
- Log errors with enough detail to debug Rube issues, but without leaking sensitive data.

---

## 9. Future Extensions (not for MVP, but keep in mind)

- Optional `POST /api/designer/proxy` to forward questions to a Project Designer Agent.
- Simple API key auth on all endpoints.
- Additional repo-related helpers (e.g., diff summaries, branches, etc.).
