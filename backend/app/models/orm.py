from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float,
    Date, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.models.database import Base


class Agency(Base):
    __tablename__ = "agencies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    city = Column(String(255), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    managers = relationship("AgencyManager", back_populates="agency", cascade="all, delete-orphan")
    agency_kpis = relationship("AgencyKPI", back_populates="agency", cascade="all, delete-orphan")
    monthly_targets = relationship("MonthlyTarget", back_populates="agency", cascade="all, delete-orphan")
    monthly_results = relationship("MonthlyResult", back_populates="agency", cascade="all, delete-orphan")
    monthly_reviews = relationship("MonthlyReview", back_populates="agency", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="agency", cascade="all, delete-orphan")


class AgencyManager(Base):
    __tablename__ = "agency_managers"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    agency = relationship("Agency", back_populates="managers")


class KPI(Base):
    __tablename__ = "kpis"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    label = Column(String(255), nullable=True)
    unit = Column(String(50), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    agency_kpis = relationship("AgencyKPI", back_populates="kpi")
    monthly_targets = relationship("MonthlyTarget", back_populates="kpi")
    monthly_results = relationship("MonthlyResult", back_populates="kpi")


class AgencyKPI(Base):
    __tablename__ = "agency_kpis"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    kpi_id = Column(Integer, ForeignKey("kpis.id", ondelete="CASCADE"), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint('agency_id', 'kpi_id', name='uq_agency_kpi'),
    )

    agency = relationship("Agency", back_populates="agency_kpis")
    kpi = relationship("KPI", back_populates="agency_kpis")


class MonthlyTarget(Base):
    __tablename__ = "monthly_targets"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    kpi_id = Column(Integer, ForeignKey("kpis.id", ondelete="CASCADE"), nullable=False)
    target_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('agency_id', 'year', 'month', 'kpi_id', name='uq_monthly_target'),
    )

    agency = relationship("Agency", back_populates="monthly_targets")
    kpi = relationship("KPI", back_populates="monthly_targets")


class MonthlyResult(Base):
    __tablename__ = "monthly_results"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    kpi_id = Column(Integer, ForeignKey("kpis.id", ondelete="CASCADE"), nullable=False)
    actual_value = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    recorded_by = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint('agency_id', 'year', 'month', 'kpi_id', name='uq_monthly_result'),
    )

    agency = relationship("Agency", back_populates="monthly_results")
    kpi = relationship("KPI", back_populates="monthly_results")


class MonthlyReview(Base):
    __tablename__ = "monthly_reviews"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    review_date = Column(Date, nullable=True)
    what_happened = Column(Text, nullable=True)
    improvement_plan = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint('agency_id', 'year', 'month', name='uq_monthly_review'),
    )

    agency = relationship("Agency", back_populates="monthly_reviews")


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    done = Column(Boolean, default=False, nullable=False)
    done_at = Column(DateTime, nullable=True)

    agency = relationship("Agency", back_populates="action_items")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="NORMAL")
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    user_agencies = relationship("UserAgency", back_populates="user", cascade="all, delete-orphan")
    security_countries = relationship("UserSecurityCountry", back_populates="user", cascade="all, delete-orphan")


class UserAgency(Base):
    __tablename__ = "user_agencies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agency_id = Column(Integer, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'agency_id', name='uq_user_agency'),
    )

    user = relationship("User", back_populates="user_agencies")
    agency = relationship("Agency")


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    region = Column(String(20), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    user_security_countries = relationship("UserSecurityCountry", back_populates="country")


class UserSecurityCountry(Base):
    __tablename__ = "user_security_countries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'country_id', name='uq_user_security_country'),
    )

    user = relationship("User", back_populates="security_countries")
    country = relationship("Country", back_populates="user_security_countries")
