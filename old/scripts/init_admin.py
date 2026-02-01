"""
Script to create the initial admin user.
Idempotent: will skip if admin already exists.

Usage:
    python -m scripts.init_admin

You will be prompted to enter:
    - Admin username
    - Admin password
    - Admin email (optional)
"""
import sys
import os
import getpass

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import User
from services.auth_service import hash_password


def create_admin():
    """
    Create the initial admin user interactively.
    """
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            print(f"✅ Admin ya existe: {existing_admin.username}")
            return

        print("\n🔐 Crear usuario administrador")
        print("=" * 40)

        # Get username
        while True:
            username = input("\nNombre de usuario: ").strip()
            if not username:
                print("El nombre de usuario no puede estar vacío.")
                continue
            
            # Check if username already exists
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                print(f"El usuario '{username}' ya existe.")
                continue
            
            break

        # Get password
        while True:
            password = getpass.getpass("Contraseña (mín. 8 caracteres): ")
            if len(password) < 8:
                print("La contraseña debe tener al menos 8 caracteres.")
                continue
            
            confirm = getpass.getpass("Confirmar contraseña: ")
            if password != confirm:
                print("Las contraseñas no coinciden.")
                continue
            
            break

        # Create admin user
        admin_user = User(
            username=username,
            password_hash=hash_password(password),
            role="admin",
            active=True
        )
        db.add(admin_user)
        db.commit()

        print(f"\n✅ Usuario administrador '{username}' creado correctamente.")
        print("\nYa puedes iniciar sesión con:")
        print(f"  Usuario: {username}")
        print(f"  Contraseña: (la que ingresaste)")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
