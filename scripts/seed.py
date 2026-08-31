#!/usr/bin/env python3
"""
Standalone seed script. Run from the backend/ directory:

    python ../scripts/seed.py

Creates all tables (if missing) and loads the curated skill/resource/project
catalog plus the demo learners, without needing to start the API server.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.session import Base, SessionLocal, engine  # noqa: E402
from app.db.seed import seed_if_empty, seed_demo_learner  # noqa: E402

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
        for role in ["AI Engineer", "Data Scientist", "Full Stack Developer", "Cybersecurity Analyst"]:
            user = seed_demo_learner(db, role)
            print(f"Seeded demo learner for {role}: {user.email}")
        print("Seeding complete.")
    finally:
        db.close()
