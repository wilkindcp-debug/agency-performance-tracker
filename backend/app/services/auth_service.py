from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.orm import User, UserSecurityCountry, Country
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthServiceError(Exception):
    pass

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(
    db: Session,
    username: str,
    password: str,
    role: str = "NORMAL",
    active: bool = True
) -> User:
    if role not in ("ADMIN", "NORMAL"):
        raise AuthServiceError("Role must be ADMIN or NORMAL")

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise AuthServiceError(f"Username '{username}' already exists")

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

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not user.active:
        raise AuthServiceError("Account is deactivated")

    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining = (user.locked_until - datetime.utcnow()).seconds // 60
        raise AuthServiceError(f"Account locked. Try again in {remaining + 1} minutes")

    if not verify_password(password, user.password_hash):
        user.failed_attempts += 1

        if user.failed_attempts >= settings.MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
            db.commit()
            raise AuthServiceError(f"Account locked for {settings.LOCKOUT_DURATION_MINUTES} minutes due to multiple failed attempts")

        db.commit()
        return None

    user.failed_attempts = 0
    user.locked_until = None
    db.commit()

    return user

def needs_security_setup(db: Session, user_id: int) -> bool:
    count = db.query(UserSecurityCountry).filter(
        UserSecurityCountry.user_id == user_id
    ).count()
    return count < settings.REQUIRED_SECURITY_COUNTRIES

def assign_security_countries(db: Session, user_id: int, country_ids: List[int]) -> None:
    if len(country_ids) != settings.REQUIRED_SECURITY_COUNTRIES:
        raise AuthServiceError(f"Must select exactly {settings.REQUIRED_SECURITY_COUNTRIES} countries")

    if len(set(country_ids)) != settings.REQUIRED_SECURITY_COUNTRIES:
        raise AuthServiceError("Cannot select the same country more than once")

    valid_countries = db.query(Country).filter(
        Country.id.in_(country_ids),
        Country.active == True
    ).count()

    if valid_countries != settings.REQUIRED_SECURITY_COUNTRIES:
        raise AuthServiceError("Some selected countries are invalid")

    db.query(UserSecurityCountry).filter(
        UserSecurityCountry.user_id == user_id
    ).delete()

    for country_id in country_ids:
        user_country = UserSecurityCountry(
            user_id=user_id,
            country_id=country_id
        )
        db.add(user_country)

    db.commit()

def get_user_security_country_ids(db: Session, user_id: int) -> List[int]:
    countries = db.query(UserSecurityCountry).filter(
        UserSecurityCountry.user_id == user_id
    ).all()
    return [c.country_id for c in countries]

def verify_security_countries(db: Session, user_id: int, selected_country_ids: List[int]) -> bool:
    correct_ids = set(get_user_security_country_ids(db, user_id))
    selected_ids = set(selected_country_ids)

    correct_count = len(correct_ids & selected_ids)
    return correct_count >= settings.MIN_CORRECT_COUNTRIES_FOR_RECOVERY

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def reset_password(db: Session, user_id: int, new_password: str) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.password_hash = hash_password(new_password)
        user.failed_attempts = 0
        user.locked_until = None
        db.commit()

def list_users(db: Session) -> List[User]:
    return db.query(User).order_by(User.username).all()

def toggle_user_active(db: Session, user_id: int, active: bool) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.active = active
        db.commit()

def update_user_role(db: Session, user_id: int, role: str) -> None:
    if role not in ("ADMIN", "NORMAL"):
        raise AuthServiceError("Role must be ADMIN or NORMAL")

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.role = role
        db.commit()

def ensure_admin_exists(db: Session) -> None:
    admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
    if not admin:
        admin = User(
            username=settings.ADMIN_USERNAME,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role="ADMIN",
            active=True
        )
        db.add(admin)
        db.commit()
