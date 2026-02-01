"""
Country Service - Country catalog management for security recovery.
"""
from typing import List, Optional, Dict, Any
import random
from db.database import SessionLocal
from db.models import Country


# Countries catalog - Africa and Latin America (remesas business context)
COUNTRIES_DATA = [
    # AFRICA
    {"name": "Senegal", "region": "AFRICA"},
    {"name": "Mali", "region": "AFRICA"},
    {"name": "Costa de Marfil", "region": "AFRICA"},
    {"name": "Camerún", "region": "AFRICA"},
    {"name": "Ghana", "region": "AFRICA"},
    {"name": "Nigeria", "region": "AFRICA"},
    {"name": "Kenia", "region": "AFRICA"},
    {"name": "Marruecos", "region": "AFRICA"},
    {"name": "Túnez", "region": "AFRICA"},
    {"name": "Etiopía", "region": "AFRICA"},
    {"name": "Tanzania", "region": "AFRICA"},
    {"name": "Uganda", "region": "AFRICA"},
    {"name": "Congo", "region": "AFRICA"},
    {"name": "Burkina Faso", "region": "AFRICA"},
    {"name": "Gambia", "region": "AFRICA"},

    # LATAM
    {"name": "México", "region": "LATAM"},
    {"name": "Guatemala", "region": "LATAM"},
    {"name": "Honduras", "region": "LATAM"},
    {"name": "El Salvador", "region": "LATAM"},
    {"name": "Nicaragua", "region": "LATAM"},
    {"name": "Colombia", "region": "LATAM"},
    {"name": "Ecuador", "region": "LATAM"},
    {"name": "Perú", "region": "LATAM"},
    {"name": "Bolivia", "region": "LATAM"},
    {"name": "Paraguay", "region": "LATAM"},
    {"name": "República Dominicana", "region": "LATAM"},
    {"name": "Cuba", "region": "LATAM"},
    {"name": "Haití", "region": "LATAM"},
    {"name": "Brasil", "region": "LATAM"},
    {"name": "Argentina", "region": "LATAM"},
]


def seed_countries() -> None:
    """
    Seed the database with countries.
    Idempotent: skips existing countries.
    """
    db = SessionLocal()
    try:
        created = 0
        skipped = 0

        for country_data in COUNTRIES_DATA:
            existing = db.query(Country).filter(
                Country.name == country_data["name"]
            ).first()

            if existing:
                skipped += 1
            else:
                country = Country(
                    name=country_data["name"],
                    region=country_data["region"],
                    active=True
                )
                db.add(country)
                created += 1

        db.commit()
        print(f"Países: {created} creados, {skipped} ya existían")

    except Exception as e:
        db.rollback()
        print(f"Error al crear países: {e}")
    finally:
        db.close()


def get_random_countries(
    limit: int = 12,
    include_ids: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """
    Get random countries for security setup or recovery.

    Args:
        limit: Total number of countries to return
        include_ids: List of country IDs that MUST be included

    Returns:
        List of country dicts, shuffled randomly
    """
    db = SessionLocal()
    try:
        # Get all active countries
        all_countries = db.query(Country).filter(Country.active == True).all()

        if not all_countries:
            return []

        result = []
        remaining_limit = limit

        # First, include required countries
        if include_ids:
            for country in all_countries:
                if country.id in include_ids:
                    result.append({
                        "id": country.id,
                        "name": country.name,
                        "region": country.region
                    })
                    remaining_limit -= 1

        # Then, add random countries to fill the limit
        other_countries = [c for c in all_countries if not include_ids or c.id not in include_ids]
        random.shuffle(other_countries)

        for country in other_countries[:remaining_limit]:
            result.append({
                "id": country.id,
                "name": country.name,
                "region": country.region
            })

        # Shuffle the final result
        random.shuffle(result)
        return result

    finally:
        db.close()


def get_countries_for_setup(limit: int = 15) -> List[Dict[str, Any]]:
    """
    Get countries for initial security setup.
    Returns a mix of Africa and LATAM countries.

    Args:
        limit: Number of countries to return

    Returns:
        List of country dicts
    """
    db = SessionLocal()
    try:
        # Get countries from both regions
        africa = db.query(Country).filter(
            Country.active == True,
            Country.region == "AFRICA"
        ).all()

        latam = db.query(Country).filter(
            Country.active == True,
            Country.region == "LATAM"
        ).all()

        # Mix both regions (roughly half and half)
        half = limit // 2
        random.shuffle(africa)
        random.shuffle(latam)

        selected = africa[:half] + latam[:limit - half]
        random.shuffle(selected)

        return [
            {
                "id": c.id,
                "name": c.name,
                "region": c.region
            }
            for c in selected
        ]

    finally:
        db.close()


def get_countries_for_recovery(
    user_correct_ids: List[int],
    total: int = 10
) -> List[Dict[str, Any]]:
    """
    Get countries for password recovery.
    Includes all correct countries plus random decoys.

    Args:
        user_correct_ids: The user's actual security country IDs
        total: Total number of countries to show

    Returns:
        Shuffled list of country dicts
    """
    db = SessionLocal()
    try:
        # Get all active countries
        all_countries = db.query(Country).filter(Country.active == True).all()

        result = []

        # Include all correct countries
        for country in all_countries:
            if country.id in user_correct_ids:
                result.append({
                    "id": country.id,
                    "name": country.name,
                    "region": country.region
                })

        # Add decoy countries
        decoys_needed = total - len(result)
        decoy_candidates = [c for c in all_countries if c.id not in user_correct_ids]
        random.shuffle(decoy_candidates)

        for country in decoy_candidates[:decoys_needed]:
            result.append({
                "id": country.id,
                "name": country.name,
                "region": country.region
            })

        # Shuffle so correct ones aren't grouped together
        random.shuffle(result)
        return result

    finally:
        db.close()


def get_country_by_id(country_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a country by ID.

    Args:
        country_id: Country ID

    Returns:
        Country dict or None
    """
    db = SessionLocal()
    try:
        country = db.query(Country).filter(Country.id == country_id).first()
        if country:
            return {
                "id": country.id,
                "name": country.name,
                "region": country.region
            }
        return None
    finally:
        db.close()


def list_all_countries() -> List[Dict[str, Any]]:
    """
    List all active countries.

    Returns:
        List of country dicts
    """
    db = SessionLocal()
    try:
        countries = db.query(Country).filter(
            Country.active == True
        ).order_by(Country.name).all()

        return [
            {
                "id": c.id,
                "name": c.name,
                "region": c.region
            }
            for c in countries
        ]
    finally:
        db.close()
