"""
Dashboard Routes
Aggregated stats and alerts for the authenticated user
"""

from datetime import datetime, date, timezone
from flask import Blueprint, g
from app.services.auth_service import auth_required
from app.models.medication import UserMedication, FoodLog, InteractionCheck
from app.services.openfda_service import get_drug_recalls
from app.services.interaction_service import get_drug_interactions
from app.errors import api_response, handle_exceptions

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/summary', methods=['GET'])
@auth_required
@handle_exceptions
def get_summary():
    """
    Get aggregated dashboard summary for the current user

    Returns:
        - medication count (active / total)
        - today's nutrition totals
        - recent interaction checks
        - food diary streak
    """
    user_id = g.current_user.id
    today = date.today()

    # Medication counts
    total_meds = UserMedication.query.filter_by(user_id=user_id).count()
    active_meds = UserMedication.query.filter_by(user_id=user_id, is_active=True).count()

    # Today's nutrition
    daily_totals = FoodLog.get_daily_totals(user_id, today)

    # Recent interaction checks (last 5)
    recent_checks = InteractionCheck.get_user_history(user_id, limit=5)

    # Food diary streak
    from app import db
    from sqlalchemy import func
    streak = 0
    check_date = today
    while True:
        has_logs = FoodLog.query.filter_by(user_id=user_id).filter(
            func.date(FoodLog.logged_date) == check_date
        ).first()
        if has_logs:
            streak += 1
            check_date = date.fromordinal(check_date.toordinal() - 1)
        else:
            break

    return api_response(
        data={
            "medications": {
                "total": total_meds,
                "active": active_meds
            },
            "nutrition_today": daily_totals,
            "recent_checks": [c.to_dict() for c in recent_checks],
            "food_diary_streak": streak,
            "user": {
                "first_name": g.current_user.first_name,
                "member_since": g.current_user.created_at.isoformat() if g.current_user.created_at else None
            }
        },
        meta={"request_id": g.request_id}
    )


@dashboard_bp.route('/alerts', methods=['GET'])
@auth_required
@handle_exceptions
def get_alerts():
    """
    Get active alerts for the user:
      - Drug recall notices for user's medications
      - High-severity interactions from today's food log
    """
    user_id = g.current_user.id
    today = date.today()
    alerts = []

    # Check for drug recalls on user's active medications
    active_meds = UserMedication.get_user_medications(user_id, active_only=True)
    for med in active_meds:
        try:
            recall_result = get_drug_recalls(med.drug_name, limit=1)
            if recall_result.get('success') and recall_result.get('count', 0) > 0:
                for recall in recall_result.get('recalls', []):
                    alerts.append({
                        "type": "recall",
                        "severity": "high",
                        "medication": med.drug_name,
                        "title": f"Recall alert for {med.drug_name}",
                        "message": recall.get('reason', 'See details'),
                        "classification": recall.get('classification'),
                        "date": recall.get('recall_date')
                    })
        except Exception:
            pass  # Don't fail the whole endpoint if one recall check fails

    # Check today's food logs for high-severity interactions
    from sqlalchemy import func
    today_foods = FoodLog.query.filter_by(user_id=user_id).filter(
        func.date(FoodLog.logged_date) == today
    ).all()

    med_names = UserMedication.get_user_medication_names(user_id, active_only=True)

    if today_foods and med_names:
        from app.services.interaction_service import check_food_against_medications
        checked_foods = set()
        for food_log in today_foods:
            food_name = food_log.food_name.lower()
            if food_name in checked_foods:
                continue
            checked_foods.add(food_name)

            try:
                result = check_food_against_medications(food_name, med_names)
                for warning in result.get('warnings', []):
                    if warning.get('severity') == 'high':
                        alerts.append({
                            "type": "interaction",
                            "severity": "high",
                            "food": food_name,
                            "medication": warning.get('drug', ''),
                            "title": f"High-risk interaction: {food_name}",
                            "message": warning.get('effect', 'Potential interaction detected'),
                            "recommendation": warning.get('recommendation', '')
                        })
            except Exception:
                pass

    return api_response(
        data={
            "alert_count": len(alerts),
            "alerts": alerts
        },
        meta={"request_id": g.request_id}
    )
