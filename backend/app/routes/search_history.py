"""
Search History Routes
Exposes the existing SearchHistory model with GET and DELETE endpoints
"""

from flask import Blueprint, request, g
from app.services.auth_service import auth_required
from app.models.medication import SearchHistory
from app import db
from app.errors import api_response, handle_exceptions

search_history_bp = Blueprint('search_history', __name__)


@search_history_bp.route('', methods=['GET'])
@auth_required
@handle_exceptions
def get_search_history():
    """
    Get the current user's search history

    Query Params:
        limit (int): Max results, default 50, max 200
        search_type (str): Filter by type (drug, food, interaction)
    """
    limit = min(max(request.args.get('limit', 50, type=int), 1), 200)
    search_type = request.args.get('search_type', '').strip().lower()

    query = SearchHistory.query.filter_by(user_id=g.current_user.id)

    if search_type:
        query = query.filter_by(search_type=search_type)

    history = query.order_by(SearchHistory.searched_at.desc()).limit(limit).all()

    return api_response(
        data={
            "history": [h.to_dict() for h in history],
            "count": len(history)
        },
        meta={"request_id": g.request_id}
    )


@search_history_bp.route('', methods=['DELETE'])
@auth_required
@handle_exceptions
def clear_search_history():
    """
    Clear all search history for the current user

    Returns:
        { data: { deleted_count }, meta: {...} }
    """
    deleted_count = SearchHistory.query.filter_by(
        user_id=g.current_user.id
    ).delete()
    db.session.commit()

    return api_response(
        data={"deleted_count": deleted_count},
        meta={"request_id": g.request_id}
    )
