# Document Processing Agent: project context

## What we are building
A web app that reads business documents (PDF, JPG, PNG), extracts their data with OCR and AI,
validates it with code, flags missing or suspicious fields, shows a dashboard of processed and
failed documents, and exports Excel and CSV. Users are accountants at Indian small businesses and
CA firms. They are not technical.

## Pipeline (every document goes through these stages in order)
1. intake: check extension AND magic bytes, size, emptiness; compute sha256; store the original
file; status = queued
2. read: PDF text layer via pypdfium2; if under 40 non-whitespace characters, render pages at 300
DPI and OCR them with Tesseract. Images are cleaned (EXIF rotation, grayscale, upscale small
images, autocontrast) and OCR'd
3. classify: weighted keyword scoring, confirmed by the AI
4. extract: Claude (structured outputs with a JSON schema) reads the OCR text plus page images; a
regex rules extractor runs too; the AI value wins, rules fill gaps; each field records its source:
ai | rules | edited
5. validate: pure Python rules, never AI; any error-level flag means needs_review
6. result: status is exactly one of valid, needs_review, failed

## Stack
- backend/: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, pypdfium2, pytesseract,
Pillow, anthropic SDK, openpyxl, pytest
- frontend/: Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, recharts
- Supabase: Postgres (database), Storage (private bucket "documents"), Auth
- Worker: backend/app/worker.py, a separate process (python -m app.worker) that claims queued
documents with SELECT ... FOR UPDATE SKIP LOCKED
- Hosting: Vercel (frontend), Render (API + worker from one Docker image)
- Do NOT use PyMuPDF/fitz (AGPL licence), Celery or Redis.

## Non-negotiable rules
1. AI reads, code checks. Validation code never calls an AI model.
2. Money is Decimal in Python and numeric(14,2) in Postgres. Never float. Amounts travel to the
browser as strings.
3. Every failed document has failure_stage and a plain-English failure_reason telling the user
what to do.
4. The original file is stored before any processing. Files are never public; the browser only
gets signed URLs that expire in 10 minutes.
5. Secrets live only in .env files. The Supabase service-role key and the Anthropic key are used
only in the backend.
6. Every pipeline stage writes a processing_events row with its duration.
7. intake.py, gstin.py, classify.py, extract_rules.py and validate.py are pure functions (no
database, no network) with pytest tests.
8. Every field edit is stored in field_edits (old value, new value, who, when) and re-runs
validation.
9. Dates printed as dd/mm/yyyy are day-first (Indian format). The UI shows amounts with Indian
grouping (en-IN), for example ₹1,23,456.00.
10. Do not modify files outside the scope of the current task. Never delete or weaken tests. Never
put sample or mock data in app code.

## Statuses
queued -> processing -> valid | needs_review | failed. needs_review <-> valid after edits. failed
-> queued on retry.

## Folder layout
backend/app/{main,config,db,models,schemas,storage,auth,worker}.py
backend/app/api/{documents,dashboard,export}.py
backend/app/pipeline/{intake,reader,gstin,classify,extract_rules,extract_ai,validate,runner}.py
backend/{alembic,scripts,tests}/ backend/Dockerfile backend/requirements.txt
frontend/app/{page.tsx, upload/, documents/, documents/[id]/, login/} frontend/lib/api.ts
frontend/e2e/
samples/{generate_samples.py, files/, expected.json} real-samples/ (git-ignored)

