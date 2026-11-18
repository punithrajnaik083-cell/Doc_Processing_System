"""Script to verify database connection and Supabase storage bucket."""
import os
import sys
import uuid

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text

from app.config import settings
from app.db import engine
from app.storage import ensure_bucket, upload, signed_url, delete

def main():
    print("=" * 60)
    print("Checking Database Connection...")
    print("=" * 60)
    if not settings.DATABASE_URL:
        print("ERROR: DATABASE_URL is not set in backend/.env")
        sys.exit(1)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), current_user;"))
            row = result.fetchone()
            print(f"Connected to database: {row[0]} as user: {row[1]}")

            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"Tables found ({len(tables)}): {', '.join(sorted(tables))}")

            expected_tables = {
                "batches",
                "documents",
                "extracted_fields",
                "validation_flags",
                "processing_events",
                "field_edits",
                "worker_heartbeat",
            }
            missing = expected_tables - set(tables)
            if missing:
                print(f"WARNING: Missing expected tables: {missing}")
                print("Run 'alembic upgrade head' to apply migrations.")
            else:
                print("All 7 expected tables are present in the database.")
    except Exception as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Checking Supabase Storage...")
    print("=" * 60)
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        print("ERROR: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is not set in backend/.env")
        sys.exit(1)

    try:
        print(f"Ensuring bucket '{settings.STORAGE_BUCKET}' exists and is private...")
        ensure_bucket()
        print(f"Bucket '{settings.STORAGE_BUCKET}' verified.")

        test_path = f"test_{uuid.uuid4().hex[:8]}.txt"
        test_content = b"Document Processing Agent Setup Check"
        print(f"Uploading test file '{test_path}'...")
        upload(test_path, test_content, "text/plain")

        print("Generating signed URL...")
        url = signed_url(test_path, expires_seconds=600)
        print(f"Signed URL (expires in 10 mins):\n{url}\n")

        print("Cleaning up test file...")
        delete([test_path])
        print("Test file deleted successfully.")
        print("\nStorage check PASSED!")
    except Exception as e:
        print(f"Storage check failed: {e}")
        sys.exit(1)

    print("\nAll checks completed successfully!")

if __name__ == "__main__":
    main()

