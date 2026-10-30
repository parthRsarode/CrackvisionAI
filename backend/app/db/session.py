import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "crackvision.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_migrations(engine_instance):
    """
    Safe lightweight migration for existing SQLite database files.
    Adds missing columns to tables if they were created before schema updates.
    """
    from sqlalchemy import text
    with engine_instance.connect() as conn:
        # Check assets table columns
        try:
            res = conn.execute(text("PRAGMA table_info(assets)"))
            existing_cols = {row[1] for row in res.fetchall()}
            if existing_cols:
                if "building_type" not in existing_cols:
                    conn.execute(text("ALTER TABLE assets ADD COLUMN building_type VARCHAR(64) DEFAULT 'residential'"))
                if "construction_year" not in existing_cols:
                    conn.execute(text("ALTER TABLE assets ADD COLUMN construction_year INTEGER"))
                if "structural_system" not in existing_cols:
                    conn.execute(text("ALTER TABLE assets ADD COLUMN structural_system VARCHAR(128) DEFAULT 'unknown'"))
                if "structural_material" not in existing_cols:
                    conn.execute(text("ALTER TABLE assets ADD COLUMN structural_material VARCHAR(128) DEFAULT 'reinforced_concrete'"))
                conn.commit()
        except Exception as e:
            pass

        # Check surveys table columns
        try:
            res = conn.execute(text("PRAGMA table_info(surveys)"))
            existing_cols = {row[1] for row in res.fetchall()}
            if existing_cols:
                if "building_profile_json" not in existing_cols:
                    conn.execute(text("ALTER TABLE surveys ADD COLUMN building_profile_json TEXT DEFAULT '{}'"))
                if "age_deterioration_context_json" not in existing_cols:
                    conn.execute(text("ALTER TABLE surveys ADD COLUMN age_deterioration_context_json TEXT DEFAULT '{}'"))
                conn.commit()
        except Exception as e:
            pass

def init_db():
    Base.metadata.create_all(bind=engine)
    run_migrations(engine)
