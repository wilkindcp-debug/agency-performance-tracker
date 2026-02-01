"""
Authentication Service - User authentication, password management, and security.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from db.database import SessionLocal
from db.models import User, UserSecurityCountry, Country


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_DURATION_MINUTES = 15
REQUIRED_SECURITY_COUNTRIES = 5
MIN_CORRECT_COUNTRIES_FOR_RECOVERY = 3


class AuthServiceError(Exception):
    """Custom exception for auth service errors."""
    pass


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored password hash

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_user(
    username: str,
    password: str,
    role: str = "NORMAL",
    active: bool = True
) -> User:
    """
    Create a new user with hashed password.

    Args:
        username: Unique username
        password: Plain text password (will be hashed)
        role: User role (ADMIN or NORMAL)
        active: Whether user is active

    Returns:
        Created User object

    Raises:
        AuthServiceError: If username already exists
    """
    if role not in ("ADMIN", "NORMAL"):
        raise AuthServiceError("El rol debe ser ADMIN o NORMAL")

    db = SessionLocal()
    try:
        # Check if username exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise AuthServiceError(f"El usuario '{username}' ya existe")

        user = User(
            username=username,
            password_hash=hash_password(password),
            role=role,
            active=active
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except AuthServiceError:
        raise
    except Exception as e:
        db.rollback()
        raise AuthServiceError(f"Error al crear usuario: {str(e)}")
    finally:
        db.close()


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user with username and password.

    Args:
        username: Username to authenticate
        password: Plain text password

    Returns:
        User dict if authentication successful, None otherwise

    Raises:
        AuthServiceError: If account is locked or other error
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()

        if not user:
            return None

        if not user.active:
            raise AuthServiceError("Esta cuenta está desactivada")

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining = (user.locked_until - datetime.utcnow()).seconds // 60
            raise AuthServiceError(f"Cuenta bloqueada. Intente de nuevo en {remaining + 1} minutos")

        # Verify password
        if not verify_password(password, user.password_hash):
            # Increment failed attempts
            user.failed_attempts += 1

            if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                db.commit()
                raise AuthServiceError(f"Cuenta bloqueada por {LOCKOUT_DURATION_MINUTES} minutos debido a múltiples intentos fallidos")

            db.commit()
            return None

        # Reset failed attempts on successful login
        user.failed_attempts = 0
        user.locked_until = None
        db.commit()

        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "active": user.active
        }

    except AuthServiceError:
        raise
    except Exception as e:
        db.rollback()
        raise AuthServiceError(f"Error de autenticación: {str(e)}")
    finally:
        db.close()


def needs_security_setup(user_id: int) -> bool:
    """
    Check if user needs to configure security countries.

    Args:
        user_id: User ID to check

    Returns:
        True if user has not configured 5 security countries
    """
    db = SessionLocal()
    try:
        count = db.query(UserSecurityCountry).filter(
            UserSecurityCountry.user_id == user_id
        ).count()
        return count < REQUIRED_SECURITY_COUNTRIES
    finally:
        db.close()


def assign_security_countries(user_id: int, country_ids: List[int]) -> None:
    """
    Assign security countries to a user.

    Args:
        user_id: User ID
        country_ids: List of exactly 5 country IDs

    Raises:
        AuthServiceError: If not exactly 5 countries or invalid countries
    """
    if len(country_ids) != REQUIRED_SECURITY_COUNTRIES:
        raise AuthServiceError(f"Debe seleccionar exactamente {REQUIRED_SECURITY_COUNTRIES} países")

    if len(set(country_ids)) != REQUIRED_SECURITY_COUNTRIES:
        raise AuthServiceError("No puede seleccionar el mismo país más de una vez")

    db = SessionLocal()
    try:
        # Verify all countries exist
        valid_countries = db.query(Country).filter(
            Country.id.in_(country_ids),
            Country.active == True
        ).count()

        if valid_countries != REQUIRED_SECURITY_COUNTRIES:
            raise AuthServiceError("Algunos países seleccionados no son válidos")

        # Remove existing security countries
        db.query(UserSecurityCountry).filter(
            UserSecurityCountry.user_id == user_id
        ).delete()

        # Add new security countries
        for country_id in country_ids:
            user_country = UserSecurityCountry(
                user_id=user_id,
                country_id=country_id
            )
            db.add(user_country)

        db.commit()

    except AuthServiceError:
        raise
    except Exception as e:
        db.rollback()
        raise AuthServiceError(f"Error al asignar países: {str(e)}")
    finally:
        db.close()


def get_user_security_country_ids(user_id: int) -> List[int]:
    """
    Get the security country IDs for a user.

    Args:
        user_id: User ID

    Returns:
        List of country IDs
    """
    db = SessionLocal()
    try:
        countries = db.query(UserSecurityCountry).filter(
            UserSecurityCountry.user_id == user_id
        ).all()
        return [c.country_id for c in countries]
    finally:
        db.close()


def verify_security_countries(user_id: int, selected_country_ids: List[int]) -> bool:
    """
    Verify if user selected at least 3 correct security countries.

    Args:
        user_id: User ID
        selected_country_ids: Countries selected by user

    Returns:
        True if at least 3 correct countries selected
    """
    correct_ids = set(get_user_security_country_ids(user_id))
    selected_ids = set(selected_country_ids)

    correct_count = len(correct_ids & selected_ids)
    return correct_count >= MIN_CORRECT_COUNTRIES_FOR_RECOVERY


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Get user by username.

    Args:
        username: Username to find

    Returns:
        User dict or None
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "active": user.active
            }
        return None
    finally:
        db.close()


def reset_password(user_id: int, new_password: str) -> None:
    """
    Reset a user's password.

    Args:
        user_id: User ID
        new_password: New plain text password
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.password_hash = hash_password(new_password)
            user.failed_attempts = 0
            user.locked_until = None
            db.commit()
    except Exception as e:
        db.rollback()
        raise AuthServiceError(f"Error al restablecer contraseña: {str(e)}")
    finally:
        db.close()


def increment_recovery_attempt(user_id: int) -> int:
    """
    Increment failed recovery attempts.

    Args:
        user_id: User ID

    Returns:
        Current number of failed attempts
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.failed_attempts += 1
            if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            db.commit()
            return user.failed_attempts
        return 0
    except Exception as e:
        db.rollback()
        return 0
    finally:
        db.close()


def reset_failed_attempts(user_id: int) -> None:
    """
    Reset failed attempts counter for a user.

    Args:
        user_id: User ID
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.failed_attempts = 0
            user.locked_until = None
            db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()


def list_users() -> List[Dict[str, Any]]:
    """
    List all users (for admin).

    Returns:
        List of user dicts
    """
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.username).all()
        return [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "active": u.active,
                "created_at": u.created_at,
                "has_security": db.query(UserSecurityCountry).filter(
                    UserSecurityCountry.user_id == u.id
                ).count() >= REQUIRED_SECURITY_COUNTRIES
            }
            for u in users
        ]
    finally:
        db.close()


def toggle_user_active(user_id: int, active: bool) -> None:
    """
    Activate or deactivate a user.

    Args:
        user_id: User ID
        active: New active status
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.active = active
            db.commit()
    except Exception as e:
        db.rollback()
        raise AuthServiceError(f"Error al cambiar estado: {str(e)}")
    finally:
        db.close()


def update_user_role(user_id: int, role: str) -> None:
    """
    Update a user's role.

    Args:
        user_id: User ID
        role: New role (ADMIN or NORMAL)
    """
    if role not in ("ADMIN", "NORMAL"):
        raise AuthServiceError("El rol debe ser ADMIN o NORMAL")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.role = role
            db.commit()
    except Exception as e:
        db.rollback()
        raise AuthServiceError(f"Error al cambiar rol: {str(e)}")
    finally:
        db.close()


def ensure_admin_exists() -> None:
    """
    Ensure the default admin user exists.
    Creates 'daniel' with password 'Admin2026@' if not exists.
    """
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "daniel").first()
        if not admin:
            admin = User(
                username="daniel",
                password_hash=hash_password("Admin2026@"),
                role="ADMIN",
                active=True
            )
            db.add(admin)
            db.commit()
            print("  [CREATE] Usuario admin 'daniel' creado")
        else:
            print("  [SKIP] Usuario admin 'daniel' ya existe")
    except Exception as e:
        db.rollback()
        print(f"  [ERROR] Error al crear admin: {e}")
    finally:
        db.close()
