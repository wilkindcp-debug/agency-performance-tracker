"""
SQLAlchemy ORM Models for Agency Performance Tracker.

Models:
- Agency: Represents an agency/branch
- AgencyManager: Managers of agencies (with history support)
- KPI: Key Performance Indicators definition
- AgencyKPI: Many-to-many relationship between agencies and KPIs
- MonthlyTarget: Monthly targets per agency and KPI
- MonthlyResult: Actual monthly results per agency and KPI
- MonthlyReview: Notes and feedback for monthly reviews
- ActionItem: Checklist items for action plans
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float,
    Date, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from db.database import Base


class Agency(Base):
    """
    Represents an agency or branch office.
    """
    __tablename__ = "agencies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    city = Column(String(255), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    managers = relationship("AgencyManager", back_populates="agency", cascade="all, delete-orphan")
    agency_kpis = relationship("AgencyKPI", back_populates="agency", cascade="all, delete-orphan")
    monthly_targets = relationship("MonthlyTarget", back_populates="agency", cascade="all, delete-orphan")
    monthly_results = relationship("MonthlyResult", back_populates="agency", cascade="all, delete-orphan")
    monthly_reviews = relationship("MonthlyReview", back_populates="agency", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="agency", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Agency(id={self.id}, name='{self.name}', city='{self.city}')>"


class AgencyManager(Base):
    """
    Represents a manager of an agency.
    Supports historical tracking with start_date and end_date.
    Only one manager should be active (active=True, end_date=None) per agency at a time.
    """
    __tablename__ = "agency_managers"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)  # NULL means currently active
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    agency = relationship("Agency", back_populates="managers")

    def __repr__(self):
        return f"<AgencyManager(id={self.id}, name='{self.full_name}', active={self.active})>"


class KPI(Base):
    """
    Key Performance Indicator definition.
    Examples: Capital Services (transactions), RIA (units), MG (units), CORNERS (units)
    """
    __tablename__ = "kpis"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # Capital Services, RIA, MG, CORNERS
    label = Column(String(255), nullable=True)  # Full descriptive name
    unit = Column(String(50), nullable=True)  # trx, units, etc.
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    agency_kpis = relationship("AgencyKPI", back_populates="kpi")
    monthly_targets = relationship("MonthlyTarget", back_populates="kpi")
    monthly_results = relationship("MonthlyResult", back_populates="kpi")

    def __repr__(self):
        return f"<KPI(id={self.id}, code='{self.code}', label='{self.label}')>"


class AgencyKPI(Base):
    """
    Many-to-many relationship between agencies and KPIs.
    Defines which KPIs are tracked for each agency.
    """
    __tablename__ = "agency_kpis"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    kpi_id = Column(Integer, ForeignKey("kpis.id", ondelete="CASCADE"), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Unique constraint to prevent duplicate assignments
    __table_args__ = (
        UniqueConstraint('agency_id', 'kpi_id', name='uq_agency_kpi'),
    )

    # Relationships
    agency = relationship("Agency", back_populates="agency_kpis")
    kpi = relationship("KPI", back_populates="agency_kpis")

    def __repr__(self):
        return f"<AgencyKPI(agency_id={self.agency_id}, kpi_id={self.kpi_id})>"


class MonthlyTarget(Base):
    """
    Monthly targets per agency, year, month, and KPI.
    """
    __tablename__ = "monthly_targets"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)  # e.g., 2026
    month = Column(Integer, nullable=False)  # 1-12
    kpi_id = Column(Integer, ForeignKey("kpis.id", ondelete="CASCADE"), nullable=False)
    target_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Unique constraint: one target per agency/year/month/kpi combination
    __table_args__ = (
        UniqueConstraint('agency_id', 'year', 'month', 'kpi_id', name='uq_monthly_target'),
    )

    # Relationships
    agency = relationship("Agency", back_populates="monthly_targets")
    kpi = relationship("KPI", back_populates="monthly_targets")

    def __repr__(self):
        return f"<MonthlyTarget(agency_id={self.agency_id}, {self.year}/{self.month}, kpi_id={self.kpi_id}, target={self.target_value})>"


class MonthlyResult(Base):
    """
    Actual monthly results per agency, year, month, and KPI.
    Recorded manually during monthly reviews.
    """
    __tablename__ = "monthly_results"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    kpi_id = Column(Integer, ForeignKey("kpis.id", ondelete="CASCADE"), nullable=False)
    actual_value = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    recorded_by = Column(String(255), nullable=True)  # Optional: who recorded this

    # Unique constraint: one result per agency/year/month/kpi combination
    __table_args__ = (
        UniqueConstraint('agency_id', 'year', 'month', 'kpi_id', name='uq_monthly_result'),
    )

    # Relationships
    agency = relationship("Agency", back_populates="monthly_results")
    kpi = relationship("KPI", back_populates="monthly_results")

    def __repr__(self):
        return f"<MonthlyResult(agency_id={self.agency_id}, {self.year}/{self.month}, kpi_id={self.kpi_id}, actual={self.actual_value})>"


class MonthlyReview(Base):
    """
    Monthly review notes for an agency.
    Contains 'what happened' explanations and improvement plans.
    """
    __tablename__ = "monthly_reviews"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    review_date = Column(Date, nullable=True)  # Date of the review meeting
    what_happened = Column(Text, nullable=True)  # Explanation of what happened
    improvement_plan = Column(Text, nullable=True)  # Plan for next month

    # Unique constraint: one review per agency/year/month combination
    __table_args__ = (
        UniqueConstraint('agency_id', 'year', 'month', name='uq_monthly_review'),
    )

    # Relationships
    agency = relationship("Agency", back_populates="monthly_reviews")

    def __repr__(self):
        return f"<MonthlyReview(agency_id={self.agency_id}, {self.year}/{self.month})>"


class ActionItem(Base):
    """
    Checklist items for monthly action plans.
    Can have multiple items per agency/month.
    """
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    title = Column(Text, nullable=False)  # Action item description
    done = Column(Boolean, default=False, nullable=False)
    done_at = Column(DateTime, nullable=True)  # When it was marked as done

    # Relationships
    agency = relationship("Agency", back_populates="action_items")

    def __repr__(self):
        return f"<ActionItem(id={self.id}, agency_id={self.agency_id}, '{self.title[:30]}...', done={self.done})>"


# ============== AUTHENTICATION & AUTHORIZATION MODELS ==============

class User(Base):
    """
    System users for authentication.
    Roles: ADMIN, NORMAL
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="NORMAL")  # ADMIN or NORMAL
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)

    # Relationships
    user_agencies = relationship("UserAgency", back_populates="user", cascade="all, delete-orphan")
    security_countries = relationship("UserSecurityCountry", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class UserAgency(Base):
    """
    Many-to-many relationship between users and agencies.
    Only applies to NORMAL users (ADMIN has access to all).
    """
    __tablename__ = "user_agencies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'agency_id', name='uq_user_agency'),
    )

    # Relationships
    user = relationship("User", back_populates="user_agencies")
    agency = relationship("Agency")

    def __repr__(self):
        return f"<UserAgency(user_id={self.user_id}, agency_id={self.agency_id})>"


class Country(Base):
    """
    Catalog of countries for security recovery.
    Regions: AFRICA, LATAM
    """
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    region = Column(String(20), nullable=False)  # AFRICA or LATAM
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user_security_countries = relationship("UserSecurityCountry", back_populates="country")

    def __repr__(self):
        return f"<Country(id={self.id}, name='{self.name}', region='{self.region}')>"


class UserSecurityCountry(Base):
    """
    Security countries selected by user for password recovery.
    Each user must have exactly 5 countries.
    """
    __tablename__ = "user_security_countries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'country_id', name='uq_user_security_country'),
    )

    # Relationships
    user = relationship("User", back_populates="security_countries")
    country = relationship("Country", back_populates="user_security_countries")

    def __repr__(self):
        return f"<UserSecurityCountry(user_id={self.user_id}, country_id={self.country_id})>"
