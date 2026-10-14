# Receipts app
Simple single-user web app to track work expense receipts (photo/PDF upload, OCR auto-fill, statuses, CSV/PDF export).

Env vars: `PASSWORD_HASH` (werkzeug hash), `SECRET_KEY`, `DATA_DIR`, `COOKIE_SECURE` (default 1).
Deploy: Render blueprint in `render.yaml` (Docker image includes tesseract).
