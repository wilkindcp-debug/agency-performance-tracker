from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.orm import (
    MonthlyTarget, MonthlyResult, MonthlyReview,
    ActionItem, AgencyKPI, KPI
)
from app.utils.helpers import compute_kpi_status

class TrackingServiceError(Exception):
    pass

def upsert_monthly_targets(
    db: Session,
    agency_id: int,
    year: int,
    month: int,
    targets: Dict[int, float]
) -> None:
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

def get_monthly_targets(
    db: Session,
    agency_id: int,
    year: int,
    month: int
) -> Dict[int, float]:
    targets = db.query(MonthlyTarget).filter(
        and_(
            MonthlyTarget.agency_id == agency_id,
            MonthlyTarget.year == year,
            MonthlyTarget.month == month
        )
    ).all()

    return {t.kpi_id: t.target_value for t in targets}

def copy_targets_to_all_months(
    db: Session,
    agency_id: int,
    year: int,
    source_month: int
) -> int:
    source_targets = db.query(MonthlyTarget).filter(
        and_(
            MonthlyTarget.agency_id == agency_id,
            MonthlyTarget.year == year,
            MonthlyTarget.month == source_month
        )
    ).all()

    if not source_targets:
        raise TrackingServiceError(f"No targets defined for month {source_month}")

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

def copy_targets_to_next_month(
    db: Session,
    agency_id: int,
    year: int,
    source_month: int
) -> bool:
    target_month = source_month + 1
    target_year = year

    if target_month > 12:
        target_month = 1
        target_year = year + 1

    targets = get_monthly_targets(db, agency_id, year, source_month)
    if not targets:
        raise TrackingServiceError(f"No targets defined for month {source_month}")

    upsert_monthly_targets(db, agency_id, target_year, target_month, targets)
    return True

def upsert_monthly_results(
    db: Session,
    agency_id: int,
    year: int,
    month: int,
    results: Dict[int, float],
    recorded_by: Optional[str] = None
) -> None:
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

def get_monthly_results(
    db: Session,
    agency_id: int,
    year: int,
    month: int
) -> Dict[int, float]:
    results = db.query(MonthlyResult).filter(
        and_(
            MonthlyResult.agency_id == agency_id,
            MonthlyResult.year == year,
            MonthlyResult.month == month
        )
    ).all()

    return {r.kpi_id: r.actual_value for r in results}

def upsert_monthly_review(
    db: Session,
    agency_id: int,
    year: int,
    month: int,
    review_date: Optional[date] = None,
    what_happened: Optional[str] = None,
    improvement_plan: Optional[str] = None
) -> None:
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

def get_monthly_review(
    db: Session,
    agency_id: int,
    year: int,
    month: int
) -> Optional[Dict[str, Any]]:
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

def add_action_item(
    db: Session,
    agency_id: int,
    year: int,
    month: int,
    title: str
) -> ActionItem:
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

def toggle_action_item_done(db: Session, item_id: int, done: bool) -> None:
    item = db.query(ActionItem).filter(ActionItem.id == item_id).first()
    if item:
        item.done = done
        item.done_at = datetime.utcnow() if done else None
        db.commit()

def delete_action_item(db: Session, item_id: int) -> None:
    item = db.query(ActionItem).filter(ActionItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()

def get_action_items(
    db: Session,
    agency_id: int,
    year: int,
    month: int
) -> List[Dict[str, Any]]:
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

def get_monthly_summary(
    db: Session,
    agency_id: int,
    year: int,
    month: int
) -> List[Dict[str, Any]]:
    assigned_kpis = db.query(KPI).join(AgencyKPI).filter(
        AgencyKPI.agency_id == agency_id,
        AgencyKPI.active == True
    ).all()

    targets = get_monthly_targets(db, agency_id, year, month)
    results = get_monthly_results(db, agency_id, year, month)

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
            "status": status
        })

    return summary

def get_all_agencies_summary(db: Session, year: int, month: int) -> List[Dict[str, Any]]:
    from app.services.agency_service import list_agencies

    agencies = list_agencies(db, active_only=True)
    result = []

    for agency in agencies:
        summary = get_monthly_summary(db, agency["id"], year, month)

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
            "manager_name": agency["manager"]["full_name"] if agency["manager"] else None,
            "avg_pct": avg_pct,
            "red_count": red_count,
            "yellow_count": yellow_count,
            "green_count": green_count,
            "kpi_details": summary
        })

    result.sort(key=lambda x: x["avg_pct"], reverse=True)
    return result
