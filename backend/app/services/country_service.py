from typing import List, Optional, Dict, Any
import random
from sqlalchemy.orm import Session
from app.models.orm import Country
from app.utils.constants import COUNTRIES_DATA

def seed_countries(db: Session) -> None:
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

def get_random_countries(
    db: Session,
    limit: int = 12,
    include_ids: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    all_countries = db.query(Country).filter(Country.active == True).all()

    if not all_countries:
        return []

    result = []
    remaining_limit = limit

    if include_ids:
        for country in all_countries:
            if country.id in include_ids:
                result.append({
                    "id": country.id,
                    "name": country.name,
                    "region": country.region
                })
                remaining_limit -= 1

    other_countries = [c for c in all_countries if not include_ids or c.id not in include_ids]
    random.shuffle(other_countries)

    for country in other_countries[:remaining_limit]:
        result.append({
            "id": country.id,
            "name": country.name,
            "region": country.region
        })

    random.shuffle(result)
    return result

def get_countries_for_setup(db: Session, limit: int = 15) -> List[Dict[str, Any]]:
    africa = db.query(Country).filter(
        Country.active == True,
        Country.region == "AFRICA"
    ).all()

    latam = db.query(Country).filter(
        Country.active == True,
        Country.region == "LATAM"
    ).all()

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

def get_countries_for_recovery(
    db: Session,
    user_correct_ids: List[int],
    total: int = 10
) -> List[Dict[str, Any]]:
    all_countries = db.query(Country).filter(Country.active == True).all()

    result = []

    for country in all_countries:
        if country.id in user_correct_ids:
            result.append({
                "id": country.id,
                "name": country.name,
                "region": country.region
            })

    decoys_needed = total - len(result)
    decoy_candidates = [c for c in all_countries if c.id not in user_correct_ids]
    random.shuffle(decoy_candidates)

    for country in decoy_candidates[:decoys_needed]:
        result.append({
            "id": country.id,
            "name": country.name,
            "region": country.region
        })

    random.shuffle(result)
    return result

def get_country_by_id(db: Session, country_id: int) -> Optional[Dict[str, Any]]:
    country = db.query(Country).filter(Country.id == country_id).first()
    if country:
        return {
            "id": country.id,
            "name": country.name,
            "region": country.region
        }
    return None

def list_all_countries(db: Session) -> List[Dict[str, Any]]:
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
