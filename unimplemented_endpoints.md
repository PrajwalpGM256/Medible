# Unimplemented Backend Endpoints

This document lists all the backend endpoints (found in `backend/app/routes/`) that are defined in the backend but *not* currently implemented in the frontend's API service (`src/constants/api.ts` and `src/services/api.ts`).

## Admin & Dashboard

*   **`admin.py`**
    *   `GET /api/v1/admin/users` - Get all users
    *   `PATCH /api/v1/admin/users/<id>` - Update user data/status
    *   `GET /api/v1/admin/stats` - Get admin statistics

*   **`dashboard.py`**
    *   `GET /api/v1/dashboard/summary` - Get dashboard summary data
    *   `GET /api/v1/dashboard/alerts` - Get dashboard alerts

## Drugs, Foods & Packaged Goods

*   **`drugs.py`**
    *   `GET /api/v1/drugs/adverse-events` - Get adverse events for drugs
    *   `GET /api/v1/drugs/recalls` - Get drug recall information
    *   `GET /api/v1/drugs/side-effects` - Get common side effects

*   **`foods.py`**
    *   `GET /api/v1/foods/favorites` - Get favorite foods
    *   `POST /api/v1/foods/favorites` - Add a food to favorites
    *   `DELETE /api/v1/foods/favorites/<id>` - Remove a food from favorites
    *   `GET /api/v1/foods/recent` - Get recently viewed foods
    *   `GET /api/v1/foods/unified-search` - Search across multiple food sources

*   **`packaged_foods.py`**
    *   `GET /api/v1/packaged-foods/search` - Search packaged foods
    *   `GET /api/v1/packaged-foods/barcode/<barcode>` - Look up food by barcode
    *   `GET /api/v1/packaged-foods/<off_id>` - Get OpenFoodFacts details by ID
    *   `GET /api/v1/packaged-foods/<off_id>/ingredients` - Get ingredient list
    *   `POST /api/v1/packaged-foods/check-ingredients` - Cross-check dietary requirements against ingredients

## Medications & Food Diary Data

*   **`medications.py`**
    *   `POST /api/v1/medications/check-food` - Check specific medication against a food
    *   `GET /api/v1/medications/interactions-summary` - Get summary of all possible interactions for current meds
    *   `GET /api/v1/medications/reminders` - Get medication reminders
    *   `POST /api/v1/medications/reminders` - Create a new reminder
    *   `DELETE /api/v1/medications/reminders/<id>` - Delete a reminder
    *   `POST /api/v1/medications/import` - Import medications from a list
    *   `GET /api/v1/medications/export` - Export medication list

*   **`food_diary.py`**
    *   `GET /api/v1/food-diary/weekly` - Get weekly food diary view
    *   `GET /api/v1/food-diary/streaks` - Get logging streaks
    *   `GET /api/v1/food-diary/export` - Export food diary data

## Interactions & History

*   **`interactions.py`**
    *   `GET /api/v1/interactions/food/<name>` - Get interactions triggered by a specific food
    *   `GET /api/v1/interactions/stats` - Get user interaction stats
    *   `POST /api/v1/interactions/batch-check` - Check multiple food/drug combinations
    *   `POST /api/v1/interactions/report` - Generate interaction report
    *   `GET /api/v1/interactions/health` - Check external API health status

*   **`interaction_history.py`**
    *   `GET /api/v1/interaction-history/stats` - Get statistics about past checks

*   **`search_history.py`**
    *   `GET /api/v1/search-history` - Get recent user searches
    *   `DELETE /api/v1/search-history` - Clear user search history

## Other

*   **`health.py`**
    *   `GET /api/v1/health` - Basic health check
    *   `GET /api/v1/health/ready` - Detailed readiness check
