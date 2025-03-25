"""
Script to run the FastAPI app with SQLite instead of PostgreSQL.
This is a temporary solution for testing the API without requiring Docker.
"""
import os
import subprocess
import sys
import sqlite3
import time
from pathlib import Path

# Create SQLite database directory if it doesn't exist
db_dir = Path("./sqlite_db")
db_dir.mkdir(exist_ok=True)
db_path = db_dir / "mentor_service.db"

# Create SQLite tables based on PostgreSQL schema
def create_tables():
    print("Creating SQLite database...")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create mentors table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mentors (
        id TEXT PRIMARY KEY,
        telegram_id TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        info TEXT NOT NULL
    )
    ''')
    
    # Create mentor_time table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mentor_time (
        id TEXT PRIMARY KEY,
        day INTEGER NOT NULL,
        time_start TEXT NOT NULL,
        time_end TEXT NOT NULL,
        mentor_id TEXT,
        FOREIGN KEY (mentor_id) REFERENCES mentors(id) ON DELETE CASCADE
    )
    ''')
    
    # Create requests table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS requests (
        id TEXT PRIMARY KEY,
        call_type INTEGER NOT NULL,
        time_sended TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        mentor_id TEXT,
        FOREIGN KEY (mentor_id) REFERENCES mentors(id) ON DELETE CASCADE,
        guest_id TEXT NOT NULL,
        description TEXT NOT NULL,
        call_time TIMESTAMP,
        response INTEGER NOT NULL DEFAULT 0
    )
    ''')
    
    conn.commit()
    conn.close()
    print("SQLite database created successfully!")

# Set environment variables for SQLite
def set_environment_vars():
    os.environ["APP_DATABASE_URL"] = f"sqlite:///{db_path}"
    
    # Override PostgreSQL settings with dummy values
    os.environ["APP_PG__HOST"] = "localhost"
    os.environ["APP_PG__DATABASE"] = "sqlite_db"
    os.environ["APP_PG__PORT"] = "5432"
    os.environ["APP_PG__USERNAME"] = "sqlite_user"
    os.environ["APP_PG__PASSWORD"] = "sqlite_password"
    
    # Set uvicorn settings
    os.environ["APP_UVICORN__HOST"] = "0.0.0.0"
    os.environ["APP_UVICORN__PORT"] = "8000"
    os.environ["APP_UVICORN__WORKERS"] = "1"

def main():
    # Setup SQLite database
    create_tables()
    
    # Set environment variables
    set_environment_vars()
    
    print("Starting FastAPI application with SQLite...")
    print("You can access the API documentation at:")
    print("  http://localhost:8000/docs")
    print("  http://localhost:8000/redoc")
    
    # Get the virtual environment's Python executable
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We are in a virtual environment
        python_executable = sys.executable
    else:
        # Not in a virtual environment, try to use the virtual env we set up
        venv_python = Path("./myenv/Scripts/python.exe")
        if venv_python.exists():
            python_executable = str(venv_python)
        else:
            python_executable = sys.executable
            print("Warning: Virtual environment not detected. Using system Python.")
    
    # Run uvicorn directly
    cmd = [python_executable, "-m", "uvicorn", "presentations.fastapi_app:app", 
           "--host", "0.0.0.0", "--port", "8000", "--reload"]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nStopping the server...")
    except Exception as e:
        print(f"Error running the server: {e}")

if __name__ == "__main__":
    main() 