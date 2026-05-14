# Lawmate / Virtual Lawyer — Architecture

This document describes how the **Virtual Lawyer** project is organized for reviewers, maintainers, and demos. It maps folders to responsibilities and lists the main runtime entry points.

## High-level stack

| Layer | Technology | Role |
|--------|------------|------|
| HTTP API | FastAPI (`api_complete.py`) | REST endpoints, auth, orchestration of AI and DB |
| AI / NLP | Python under `src/` | RAG, chat pipeline, document analysis, risk tools |
| Data | MongoDB via `db/` | Users, cases, chat history, admin settings |
| Web app | Next.js (`Lawmate/Lawmate/`) | Citizen, lawyer, and admin UIs |

## Repository layout

```
virtual-lawyer/
├── api_complete.py      # FastAPI application (single module; see section comments inside)
├── config.py            # Environment-driven settings (Groq, pipeline flags)
├── security_utils.py    # JWT, sanitization, role guards (optional deps)
├── requirements.txt     # Python dependencies
├── src/                 # Core AI: pipelines, RAG, chatbot, document modules
├── db/                  # Mongo client, repositories, bootstrap, seed
├── data/                # Uploads, generated docs, RAG corpora (large; often gitignored)
├── models/              # Local / fine-tuned model weights (large)
├── scripts/             # Offline tooling (see scripts/README.md)
│   ├── _repo.py         # Shared repo-root + sys.path bootstrap for subfolders
│   ├── corpus/          # RAG datasets, scraping, merge/rebuild pipelines
│   ├── training/        # Golden data + LoRA / training entrypoints
│   ├── templates/       # DOCX template and branding asset builders
│   ├── qa/              # Document/API smoke scripts and diagnostics
│   └── dev/             # venv/setup, model config fixes, cleanup utilities
├── Lawmate/Lawmate/     # Next.js frontend (App Router)
└── docs/                # Architecture and review notes (this folder)
```

## How to run (development)

1. **Backend:** from repository root, with `.env` containing `MONGODB_CONNECTION_STRING` (and keys as needed):

   ```bash
   uvicorn api_complete:app --host 0.0.0.0 --port 8000 --reload
   ```

   Or: `python api_complete.py` if the file defines a `__main__` block for the same app.

2. **Frontend:** `Lawmate/Lawmate` — set `NEXT_PUBLIC_API_URL` to the API base (e.g. `http://localhost:8000`), then `npm install` and `npm run dev`.

3. **Tooling scripts:** run from repo root so paths like `./data/` resolve. Use the subfolder layout, for example:

   ```bash
   python scripts/corpus/rebuild_rag_corpus.py
   python scripts/qa/diagnose_document_testing.py
   ```

   See **`scripts/README.md`** for a full map. Scripts that import the backend use `scripts/_repo.py` to locate the project root from any subfolder.

## Backend design (`api_complete.py`)

- **Optional imports:** Heavy or fragile dependencies (GPU, specific packages) are imported in `try` blocks so the API can still boot for document-only or DB-only demos.
- **`sys.path`:** `src/` is prepended so pipeline modules can be imported without installing a package (see comment at top of `api_complete.py`).
- **Routers:** All routes live in one file for this FYP codebase; section banners in the source group endpoints by domain (health, chat, analysis, documents, dashboards, auth, admin, marketplace).
- **OpenAPI:** FastAPI auto-generates `/docs` and `/redoc` from route handlers and Pydantic models—handler docstrings appear as operation descriptions.

## Database layer (`db/`)

- **`database.py`:** Singleton-style Mongo client and database accessors (`get_collection`).
- **`repository.py`:** All CRUD and query helpers; indexes created in `init_schema()`.
- **`bootstrap.py`:** Called at API startup: schema + optional seed data.

## Frontend (`Lawmate/Lawmate/`)

- **`app/`:** Next.js App Router routes (`citizen/`, `lawyer/`, `admin/`, auth pages).
- **`lib/api.ts`:** Central HTTP client: base URL, JWT from `localStorage`, JSON and multipart helpers.
- **`lib/services/*.ts`:** Feature-specific API calls (cases, chat, lawyers, etc.).
- **`components/`:** Shared UI (including shadcn-style primitives under `components/ui/`).

## Security notes (production)

- CORS allowlist is explicit; add deployment frontends via `FRONTEND_URL` / env.
- Admin and role-protected routes use FastAPI `Depends(...)` from `security_utils` when JWT stack is installed.
- User input for signup and rich text paths is sanitized where applied in the API layer.

## Further reading in code

- Pydantic models in `api_complete.py` define the **contract** between frontend and backend.
- `src/two_stage_pipeline.py` and related files document the **RAG + formatter** flow for legal answers.
