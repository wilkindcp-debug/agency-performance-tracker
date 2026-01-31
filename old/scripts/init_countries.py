"""
Script to initialize countries catalog.
Idempotent: will not create duplicates if run multiple times.

Usage:
    python -m scripts.init_countries
"""
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.country_service import seed_countries


def main():
    """Initialize countries catalog."""
    print("Inicializando catálogo de países...")
    seed_countries()
    print("Catálogo de países listo.")


if __name__ == "__main__":
    main()
