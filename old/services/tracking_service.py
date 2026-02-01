"""
Tracking Service - Business logic for targets, results, reviews and action items.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.database import SessionLocal
from db.models import (
    MonthlyTarget, MonthlyResult, MonthlyReview,
    ActionItem, AgencyKPI, KPI
)
from services.utils import compute_kpi_status, get_status_emoji


class TrackingServiceError(Exception):
    """Custom exception for tracking service errors."""
    pass


# ============== MONTHLY TARGETS ==============

def upsert_monthly_targets(
    agency_id: int,
    year: int,
    month: int,
    targets: Dict[int, float]
) -> None:
    """
    Create or update monthly targets for an agency.

    Args:
        agency_id: The agency ID
        year: Year (e.g., 2026)
        month: Month (1-12)
        targets: Dict mapping kpi_id to target_value
    """
    db = SessionLocal()
    try:
        for kpi_id, target_value in targets.items():
            existing = db.query(MonthlyTarget).filter(
                and_(
                    MonthlyTarget.agency_id == agency_id,
                    MonthlyTarget.year == year,
                    MonthlyTarget.month == month,
                    MonthlyTarget.kpi_id == kpi_id
                )
            ).first()

            if existing:
                existing.target_value = target_value
            else:
                new_target = MonthlyTarget(
                    agency_id=agency_id,
                    year=year,
                    month=month,
                    kpi_id=kpi_id,
                    target_value=target_value
                )
                db.add(new_target)

        db.commit()
    except Exception as e:
        db.rollback()
        raise TrackingServiceError(f"Error al guardar objetivos: {str(e)}")
    finally:
        db.close()


def get_monthly_targets(
    agency_id: int,
    year: int,
    month: int
) -> Dict[int, float]:
    """
    Get monthly targets for an agency.

    Args:
        agency_id: The agency ID
        year: Year
        month: Month (1-12)

    Returns:
        Dict mapping kpi_id to target_value
    """
    db = SessionLocal()
    try:
        targets = db.query(MonthlyTarget).filter(
            and_(
                MonthlyTarget.agency_id == agency_id,
                MonthlyTarget.year == year,
                MonthlyTarget.month == month
            )
        ).all()

        return {t.kpi_id: t.target_value for t in targets}
    finally:
        db.close()


def copy_targets_to_all_months(
    agency_id: int,
    year: int,
    source_month: int
) -> int:
    """
    Copy targets from one month to all other months of the year.

    Args:
        agency_id: The agency ID
        year: Year
        source_month: Source month to copy from

    Returns:
        Number of months updated
    """
    db = SessionLocal()
    try:
        # Get source targets
        source_targets = db.query(MonthlyTarget).filter(
            and_(
                MonthlyTarget.agency_id == agency_id,
                MonthlyTarget.year == year,
                MonthlyTarget.month == source_month
            )
        ).all()

        if not source_targets:
            raise TrackingServiceError(f"No hay objetivos definidos para el mes {source_month}")

        months_updated = 0
        for target_month in range(1, 13):
            if target_month == source_month:
                continue

            for source in source_targets:
                existing = db.query(MonthlyTarget).filter(
                    and_(
                        MonthlyTarget.agency_id == agency_id,
                        MonthlyTarget.year == year,
                        MonthlyTarget.month == target_month,
                        MonthlyTarget.kpi_id == source.kpi_id
                    )
                ).first()

                if existing:
                    existing.target_value = source.target_value
                else:
                    new_target = MonthlyTarget(
                        agency_id=agency_id,
                        year=year,
                        month=target_month,
                        kpi_id=source.kpi_id,
                        target_value=source.target_value
                    )
                    db.add(new_target)

            months_updated += 1

        db.commit()
        return months_updated

    except TrackingServiceError:
        raise
    except Exception as e:
        db.rollback()
        raise TrackingServiceError(f"Error al copiar objetivos: {str(e)}")
    finally:
        db.close()


def copy_targets_to_next_month(
    agency_id: int,
    year: int,
    source_month: int
) -> bool:
    """
    Copy targets from one month to the next month.

    Args:
        agency_id: The agency ID
        year: Year
        source_month: Source month to copy from

    Returns:
        True if successful
    """
    target_month = source_month + 1
    target_year = year

    if target_month > 12:
        target_month = 1
        target_year = year + 1

    targets = get_monthly_targets(agency_id, year, source_month)
    if not targets:
        raise TrackingServiceError(f"No hay objetivos definidos para el mes {source_month}")

    upsert_monthly_targets(agency_id, target_year, target_month, targets)
    return True


# ============== MONTHLY RESULTS ==============

def upsert_monthly_results(
    agency_id: int,
    year: int,
    month: int,
    results: Dict[int, float],
    recorded_by: Optional[str] = None
) -> None:
    """
    Create or update monthly results for an agency.

    Args:
        agency_id: The agency ID
        year: Year
        month: Month (1-12)
        results: Dict mapping kpi_id to actual_value
        recorded_by: Optional name of who recorded the results
    """
    db = SessionLocal()
    try:
        for kpi_id, actual_value in results.items():
            existing = db.query(MonthlyResult).filter(
                and_(
                    MonthlyResult.agency_id == agency_id,
                    MonthlyResult.year == year,
                    MonthlyResult.month == month,
                    MonthlyResult.kpi_id == kpi_id
                )
            ).first()

            if existing:
                existing.actual_value = actual_value
                existing.recorded_at = datetime.utcnow()
                existing.recorded_by = recorded_by
            else:
                new_result = MonthlyResult(
                    agency_id=agency_id,
                    year=year,
                    month=month,
                    kpi_id=kpi_id,
                    actual_value=actual_value,
                    recorded_by=recorded_by
                )
                db.add(new_result)

        db.commit()
    except Exception as e:
        db.rollback()
        raise TrackingServiceError(f"Error al guardar resultados: {str(e)}")
    finally:
        db.close()


def get_monthly_results(
    agency_id: int,
    year: int,
    month: int
) -> Dict[int, float]:
    """
    Get monthly results for an agency.

    Args:
        agency_id: The agency ID
        year: Year
        month: Month (1-12)

    Returns:
        Dict mapping kpi_id to actual_value
    """
    db = SessionLocal()
    try:
        results = db.query(MonthlyResult).filter(
            and_(
                MonthlyResult.agency_id == agency_id,
                MonthlyResult.year == year,
                MonthlyResult.month == month
            )
        ).all()

        return {r.kpi_id: r.actual_value for r in results}
    finally:
        db.close()


# ============== MONTHLY REVIEWS ==============

def upsert_monthly_review(
    agency_id: int,
    year: int,
    month: int,
    review_date: Optional[date] = None,
    what_happened: Optional[str] = None,
    improvement_plan: Optional[str] = None
) -> None:
    """
    Create or update a monthly review for an agency.

    Args:
        agency_id: The agency ID
        year: Year
        month: Month (1-12)
        review_date: Date of the review meeting
        what_happened: Explanation of what happened
        improvement_plan: Plan for improvement
    """
    db = SessionLocal()
    try:
        existing = db.query(MonthlyReview).filter(
            and_(
                MonthlyReview.agency_id == agency_id,
                MonthlyReview.year == year,
                MonthlyReview.month == month
            )
        ).first()

        if existing:
            if review_date is not None:
                existing.review_date = review_date
            if what_happened is not None:
                existing.what_happened = what_happened
            if improvement_plan is not None:
                existing.improvement_plan = improvement_plan
        else:
            new_review = MonthlyReview(
                agency_id=agency_id,
                year=year,
                month=month,
                review_date=review_date or date.today(),
                what_happened=what_happened or "",
                improvement_plan=improvement_plan or ""
            )
            db.add(new_review)

        db.commit()
    except Exception as e:
        db.rollback()
        raise TrackingServiceError(f"Error al guardar revisión: {str(e)}")
    finally:
        db.close()


def get_monthly_review(
    agency_id: int,
    year: int,
    month: int
) -> Optional[Dict[str, Any]]:
    """
    Get the monthly review for an agency.

    Args:
        agency_id: The agency ID
        year: Year
        month: Month (1-12)

    Returns:
        Dict with review data or None if not found
    """
    db = SessionLocal()
    try:
        review = db.query(MonthlyReview).filter(
            and_(
                MonthlyReview.agency_id == agency_id,
                MonthlyReview.year == year,
                MonthlyReview.month == month
            )
        ).first()

        if review:
            return {
                "id": review.id,
                "review_date": review.review_date,
                "what_happened": review.what_happened,
                "improvement_plan": review.improvement_plan
            }
        return None
    finally:
        db.close()


# ============== ACTION ITEMS ==============

def add_action_item(
    agency_id: int,
    year: int,
    month: int,
    title: str
) -> ActionItem:
    """
    Add a new action item to the checklist.

    Args:
        agency_id: The agency ID
        year: Year
        month: Month (1-12)
        title: Action item description

    Returns:
        Created ActionItem
    """
    db = SessionLocal()
    try:
        item = ActionItem(
            agency_id=agency_id,
            year=year,
            month=month,
            title=title,
            done=False
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    except Exception as e:
        db.rollback()
        raise TrackingServiceError(f"Error al agregar acción: {str(e)}")
    finally:
        db.close()


def toggle_action_item_done(item_id: int, done: bool) -> None:
    """
    Toggle the done status of an action item.

    Args:
        item_id: The action item ID
        done: New done status
    """
    db = SessionLocal()
    try:
        item = db.query(ActionItem).filter(ActionItem.id == item_id).first()
        if item:
            item.done = done
            item.done_at = datetime.utcnow() if done else None
            db.commit()
    except Exception as e:
        db.rollback()
        raise TrackingServiceError(f"Error al actualizar acción: {str(e)}")
    finally:
        db.close()


def delete_action_item(item_id: int) -> None:
    """
    Delete an action item.

    Args:
        item_id: The action item ID
    """
    db = SessionLocal()
    try:
        item = db.query(ActionItem).filter(ActionItem.id == item_id).first()
        if item:
            db.delete(item)
            db.commit()
    except Exception as e:
        db.rollback()
        raise TrackingServiceError(f"Error al eliminar acción: {str(e)}")
    finally:
        db.close()


def get_action_items(
    agency_id: int,
    year: int,
    month: int
) -> List[Dict[str, Any]]:
    """
    Get all action items for a month.

    Args:
        agency_id: The agency ID
        year: Year
        month: Month (1-12)

    Returns:
        List of action item dicts
    """
    db = SessionLocal()
    try:
        items = db.query(ActionItem).filter(
            and_(
                ActionItem.agency_id == agency_id,
                ActionItem.year == year,
                ActionItem.month == month
            )
        ).order_by(ActionItem.id).all()

        return [
            {
                "id": item.id,
                "title": item.title,
                "done": item.done,
                "done_at": item.done_at
            }
            for item in items
        ]
    finally:
        db.close()


# ============== SUMMARY / DASHBOARD ==============

def get_monthly_summary(
    agency_id: int,
    year: int,
    month: int
) -> List[Dict[str, Any]]:
    """
    Get a summary of targets vs results for all KPIs of an agency.

    Args:
        agency_id: The agency ID
        year: Year
        month: Month (1-12)

    Returns:
        List of dicts with KPI performance data
    """
    db = SessionLocal()
    try:
        # Get assigned KPIs
        assigned_kpis = db.query(KPI).join(AgencyKPI).filter(
            AgencyKPI.agency_id == agency_id,
            AgencyKPI.active == True
        ).all()

        targets = get_monthly_targets(agency_id, year, month)
        results = get_monthly_results(agency_id, year, month)

        summary = []
        for kpi in assigned_kpis:
            target = targets.get(kpi.id, 0)
            actual = results.get(kpi.id, 0)
            diff, pct, status = compute_kpi_status(target, actual)

            summary.append({
                "kpi_id": kpi.id,
                "kpi_code": kpi.code,
                "kpi_label": kpi.label,
                "kpi_unit": kpi.unit,
                "target": target,
                "actual": actual,
                "diff": diff,
                "pct": pct,
                "status": status,
                "status_emoji": get_status_emoji(status)
            })

        return summary
    finally:
        db.close()


def get_all_agencies_summary(year: int, month: int) -> List[Dict[str, Any]]:
    """
    Get summary of all agencies for a specific month.

    Args:
        year: Year
        month: Month (1-12)

    Returns:
        List of agency summaries with average performance
    """
    from services.agency_service import list_agencies

    agencies = list_agencies(active_only=True)
    result = []

    for agency in agencies:
        summary = get_monthly_summary(agency["id"], year, month)

        # Calculate average performance
        if summary:
            avg_pct = sum(s["pct"] for s in summary) / len(summary)
            red_count = sum(1 for s in summary if s["status"] == "red")
            yellow_count = sum(1 for s in summary if s["status"] == "yellow")
            green_count = sum(1 for s in summary if s["status"] == "green")
        else:
            avg_pct = 0
            red_count = yellow_count = green_count = 0

        result.append({
            "agency_id": agency["id"],
            "agency_name": agency["name"],
            "city": agency["city"],
            "manager_name": agency["manager"]["name"] if agency["manager"] else None,
            "avg_pct": avg_pct,
            "red_count": red_count,
            "yellow_count": yellow_count,
            "green_count": green_count,
            "kpi_details": summary
        })

    # Sort by average performance (descending)
    result.sort(key=lambda x: x["avg_pct"], reverse=True)
    return result
