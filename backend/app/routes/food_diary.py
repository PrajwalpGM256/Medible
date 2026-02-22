"""
Food Diary Routes
Handles user food logging and daily intake tracking
"""

from datetime import datetime, date, timedelta
from flask import Blueprint, request, g
from app.services.auth_service import auth_required
from app import db
from app.models.medication import FoodLog
from app.errors import api_response, BadRequestError, NotFoundError

food_diary_bp = Blueprint('food_diary', __name__)


@food_diary_bp.route('', methods=['GET'])
@auth_required
def get_food_logs():
    """
    Get user's food logs
    
    Query Params:
        date (str): Specific date (YYYY-MM-DD), defaults to today
        start_date (str): Start of date range
        end_date (str): End of date range
        days (int): Last N days, default 7
    """
    user_id = g.current_user.id
    
    # Check for specific date
    date_str = request.args.get('date')
    if date_str:
        try:
            log_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise BadRequestError("Invalid date format. Use YYYY-MM-DD", {"field": "date"})
        
        logs = FoodLog.get_user_logs_by_date(user_id, log_date)
        totals = FoodLog.get_daily_totals(user_id, log_date)
        
        return api_response({
            "date": log_date.isoformat(),
            "logs": [log.to_dict() for log in logs],
            "totals": totals
        })
    
    # Check for date range
    start_str = request.args.get('start_date')
    end_str = request.args.get('end_date')
    
    if start_str and end_str:
        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            raise BadRequestError("Invalid date format. Use YYYY-MM-DD", {"field": "date"})
    else:
        # Default to last N days
        days = request.args.get('days', 7, type=int)
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
    
    logs = FoodLog.get_user_logs_range(user_id, start_date, end_date)
    
    # Group by date
    by_date = {}
    for log in logs:
        date_key = log.logged_date.isoformat()
        if date_key not in by_date:
            by_date[date_key] = []
        by_date[date_key].append(log.to_dict())
    
    return api_response({
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "logs_by_date": by_date,
        "total_entries": len(logs)
    })


@food_diary_bp.route('/today', methods=['GET'])
@auth_required
def get_today_logs():
    """Get today's food logs with totals"""
    user_id = g.current_user.id
    today = date.today()
    
    logs = FoodLog.get_user_logs_by_date(user_id, today)
    totals = FoodLog.get_daily_totals(user_id, today)
    
    # Group by meal type
    by_meal = {"breakfast": [], "lunch": [], "dinner": [], "snack": [], "other": []}
    for log in logs:
        meal = log.meal_type or "other"
        if meal in by_meal:
            by_meal[meal].append(log.to_dict())
        else:
            by_meal["other"].append(log.to_dict())
    
    return api_response({
        "date": today.isoformat(),
        "logs": [log.to_dict() for log in logs],
        "by_meal": by_meal,
        "totals": totals
    })


@food_diary_bp.route('', methods=['POST'])
@auth_required
def add_food_log():
    """
    Add a food log entry
    
    Body:
        food_name (str): Required
        fdc_id (int): USDA food ID (optional)
        servings (float): Number of servings, default 1
        serving_size (float): Size per serving
        serving_unit (str): g, oz, cup, etc.
        calories, protein, carbs, fat, fiber, sugar, sodium (float): Nutrition
        meal_type (str): breakfast, lunch, dinner, snack
        notes (str): Optional notes
        logged_date (str): YYYY-MM-DD, defaults to today
    """
    user_id = g.current_user.id
    data = request.get_json() or {}
    
    food_name = data.get('food_name', '').strip()
    if not food_name:
        raise BadRequestError("Food name is required", {"field": "food_name"})
    
    # Parse date
    date_str = data.get('logged_date')
    if date_str:
        try:
            log_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise BadRequestError("Invalid date format. Use YYYY-MM-DD", {"field": "logged_date"})
    else:
        log_date = date.today()
    
    food_log = FoodLog(
        user_id=user_id,
        food_name=food_name,
        fdc_id=data.get('fdc_id'),
        brand_owner=data.get('brand_owner'),
        servings=data.get('servings', 1.0),
        serving_size=data.get('serving_size'),
        serving_unit=data.get('serving_unit', 'g'),
        calories=data.get('calories'),
        protein=data.get('protein'),
        carbs=data.get('carbs'),
        fat=data.get('fat'),
        fiber=data.get('fiber'),
        sugar=data.get('sugar'),
        sodium=data.get('sodium'),
        meal_type=data.get('meal_type'),
        notes=data.get('notes'),
        logged_date=log_date,
        had_interaction=data.get('had_interaction'),
        interaction_count=data.get('interaction_count', 0)
    )
    
    db.session.add(food_log)
    db.session.commit()
    
    return api_response({"food_log": food_log.to_dict()}, status_code=201)


@food_diary_bp.route('/<int:log_id>', methods=['DELETE'])
@auth_required
def delete_food_log(log_id: int):
    """Delete a food log entry"""
    user_id = g.current_user.id
    
    food_log = FoodLog.query.filter_by(id=log_id, user_id=user_id).first()
    if not food_log:
        raise NotFoundError("Food log not found", {"id": log_id})
    
    db.session.delete(food_log)
    db.session.commit()
    
    return api_response({"deleted_id": log_id})


@food_diary_bp.route('/<int:log_id>', methods=['PATCH'])
@auth_required
def update_food_log(log_id: int):
    """Update a food log entry"""
    user_id = g.current_user.id
    data = request.get_json() or {}
    
    food_log = FoodLog.query.filter_by(id=log_id, user_id=user_id).first()
    if not food_log:
        raise NotFoundError("Food log not found", {"id": log_id})
    
    # Update allowed fields
    updatable = ['food_name', 'servings', 'serving_size', 'serving_unit',
                 'calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium',
                 'meal_type', 'notes', 'had_interaction', 'interaction_count']
    
    for field in updatable:
        if field in data:
            setattr(food_log, field, data[field])
    
    db.session.commit()
    
    return api_response({"food_log": food_log.to_dict()})


@food_diary_bp.route('/summary', methods=['GET'])
@auth_required
def get_summary():
    """
    Get nutrition summary for date range
    
    Query Params:
        days (int): Number of days to summarize, default 7
    """
    user_id = g.current_user.id
    days = request.args.get('days', 7, type=int)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    daily_summaries = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        totals = FoodLog.get_daily_totals(user_id, current_date)
        totals["date"] = current_date.isoformat()
        daily_summaries.append(totals)
    
    # Calculate averages
    total_days_with_logs = sum(1 for d in daily_summaries if d["food_count"] > 0)
    
    if total_days_with_logs > 0:
        averages = {
            "calories": sum(d["calories"] for d in daily_summaries) / total_days_with_logs,
            "protein": sum(d["protein"] for d in daily_summaries) / total_days_with_logs,
            "carbs": sum(d["carbs"] for d in daily_summaries) / total_days_with_logs,
            "fat": sum(d["fat"] for d in daily_summaries) / total_days_with_logs,
        }
    else:
        averages = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    
    return api_response({
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "days": days,
        "daily_summaries": daily_summaries,
        "averages": averages,
        "days_logged": total_days_with_logs
    })


@food_diary_bp.route('/weekly', methods=['GET'])
@auth_required
def get_weekly_summary():
    """
    Get weekly nutrition summary with averages per day
    """
    user_id = g.current_user.id
    end_date = date.today()
    start_date = end_date - timedelta(days=6)

    daily_data = []
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        totals = FoodLog.get_daily_totals(user_id, current_date)
        totals["date"] = current_date.isoformat()
        totals["day_name"] = current_date.strftime("%A")
        daily_data.append(totals)

    days_with_logs = [d for d in daily_data if d["food_count"] > 0]
    count = len(days_with_logs) if days_with_logs else 1

    averages = {
        "calories": round(sum(d["calories"] for d in daily_data) / count, 1),
        "protein": round(sum(d["protein"] for d in daily_data) / count, 1),
        "carbs": round(sum(d["carbs"] for d in daily_data) / count, 1),
        "fat": round(sum(d["fat"] for d in daily_data) / count, 1),
    }

    return api_response({
        "week_start": start_date.isoformat(),
        "week_end": end_date.isoformat(),
        "daily": daily_data,
        "averages": averages,
        "days_logged": len(days_with_logs)
    })


@food_diary_bp.route('/streaks', methods=['GET'])
@auth_required
def get_streaks():
    """
    Get food diary logging streak info
    """
    from sqlalchemy import func

    user_id = g.current_user.id
    today = date.today()

    # Current streak
    current_streak = 0
    check_date = today
    while True:
        has_logs = FoodLog.query.filter_by(user_id=user_id).filter(
            func.date(FoodLog.logged_date) == check_date
        ).first()
        if has_logs:
            current_streak += 1
            check_date = date.fromordinal(check_date.toordinal() - 1)
        else:
            break

    # Total days ever logged
    total_days = db.session.query(
        func.count(func.distinct(FoodLog.logged_date))
    ).filter_by(user_id=user_id).scalar() or 0

    # Total entries
    total_entries = FoodLog.query.filter_by(user_id=user_id).count()

    return api_response({
        "current_streak": current_streak,
        "total_days_logged": total_days,
        "total_entries": total_entries,
        "today_logged": current_streak > 0
    })


@food_diary_bp.route('/export', methods=['GET'])
@auth_required
def export_food_diary():
    """
    Export food diary as JSON

    Query Params:
        days (int): Number of days to export, default 30
        format (str): 'json' (default)
    """
    user_id = g.current_user.id
    days = request.args.get('days', 30, type=int)

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    logs = FoodLog.get_user_logs_range(user_id, start_date, end_date)

    return api_response({
        "export": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_entries": len(logs),
            "logs": [log.to_dict() for log in logs]
        }
    })
