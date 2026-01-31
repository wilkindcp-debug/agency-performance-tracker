"""
Master initialization script for production deployment.
Runs all initialization scripts in the correct order.

Usage:
    python -m scripts.init_all

This script will:
    1. Create all database tables (if they don't exist)
    2. Populate countries catalog
    3. Populate default KPIs
    4. Create the admin user (interactive)
"""
import sys
import os
import subprocess

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_script(module_name, description):
    """Run a Python module as a script."""
    print(f"\n{'='*50}")
    print(f"📌 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", module_name],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {module_name}: {e}")
        return False


def main():
    """Run all initialization scripts."""
    print("\n🚀 Inicialización completa de la aplicación")
    print("="*50)
    
    scripts = [
        ("scripts.init_db_prod", "Paso 1: Crear esquema de base de datos"),
        ("scripts.init_countries", "Paso 2: Inicializar catálogo de países"),
        ("scripts.init_kpis", "Paso 3: Inicializar KPIs por defecto"),
        ("scripts.init_admin", "Paso 4: Crear usuario administrador"),
    ]
    
    results = []
    for module_name, description in scripts:
        success = run_script(module_name, description)
        results.append((description, success))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Resumen")
    print(f"{'='*50}")
    
    for description, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {description}")
    
    all_success = all(success for _, success in results)
    
    if all_success:
        print(f"\n✅ ¡Inicialización completada correctamente!")
        print("\nYa puedes ejecutar la aplicación con:")
        print("  streamlit run main.py")
    else:
        print(f"\n⚠️  Algunos pasos fallaron. Revisa los errores arriba.")
        sys.exit(1)


if __name__ == "__main__":
    main()
