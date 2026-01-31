"""
Script to initialize the database schema in production (Supabase).
Creates all tables defined in models.py.

Usage:
    python -m scripts.init_db_prod

This script is idempotent: it will create only tables that don't exist.
"""
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine, Base
from sqlalchemy import inspect


def init_database():
    """
    Initialize the database by creating all tables.
    Idempotent: skips tables that already exist.
    """
    print("⏳ Conectando a la base de datos...")
    
    try:
        # Inspect existing tables
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        
        print(f"Tablas existentes: {len(existing_tables)}")
        if existing_tables:
            for table in sorted(existing_tables):
                print(f"  - {table}")
        
        # Get all tables that should exist
        all_tables = set(Base.metadata.tables.keys())
        tables_to_create = all_tables - existing_tables
        
        if not tables_to_create:
            print("\n✅ Todas las tablas ya existen. No hay nada que hacer.")
            return
        
        print(f"\n⏳ Creando {len(tables_to_create)} tabla(s)...")
        for table in sorted(tables_to_create):
            print(f"  - {table}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("\n✅ ¡Tablas creadas correctamente!")
        print("\nTablas en la base de datos:")
        inspector = inspect(engine)
        for table in sorted(inspector.get_table_names()):
            print(f"  - {table}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nVerifica que:")
        print("  1. DATABASE_URL esté configurado correctamente")
        print("  2. La base de datos esté accesible (firewall/allowlist)")
        print("  3. Las credenciales sean válidas")
        raise


if __name__ == "__main__":
    init_database()
