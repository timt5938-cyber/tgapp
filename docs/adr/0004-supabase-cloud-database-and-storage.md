# 4. Supabase Cloud Database and Storage

The system will use Supabase as the managed cloud backend service (PostgreSQL database and Object Storage) for storing user profiles, calibrated glyphs, notebook preferences, and generated conspectus documents.

## Considered Options
- **Local SQLite + Filesystem:** Zero cloud setup, but requires persistent local server disk and lacks built-in authentication, backups, or multi-device sync.
- **Self-hosted PostgreSQL & MinIO:** Requires dedicated DevOps setup and maintenance.
- **Supabase Cloud (Selected):** Managed PostgreSQL database, built-in Storage buckets for user assets (calibration sheets, personal glyphs, PDFs), and instant REST/Realtime APIs.

## Consequences
- Project `tgapp` created in Supabase (`https://faxtkubhxjesghpduiba.supabase.co`).
- Backend connects via Supabase Python client using project URL and credentials.
- Schema migrations and tables (e.g., `users`, `user_fonts`, `conspectuses`) can be maintained directly in Supabase.
