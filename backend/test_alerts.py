import sys
import logging
import time
from app import create_app
from app.models.user import User
from flask import g
from app.routes.dashboard import get_alerts

app = create_app('development')
with app.app_context():
    user = User.query.filter_by(email='demo@medible.com').first()
    if not user:
        print("Demo user not found.")
        sys.exit(1)
        
    g.current_user = user
    g.request_id = 'test-cli'
    print(f"Testing alerts for user: {user.email}")
    
    start_time = time.time()
    try:
        response = get_alerts()
        # Handle Flask response tuple (Response, status_code)
        resp_obj = response[0] if isinstance(response, tuple) else response
        data = resp_obj.get_json()
        duration = time.time() - start_time
        print(f"Success! Response generated in {duration:.2f} seconds.")
        print(f"Total Alerts: {data['data'].get('alert_count', 0)}")
    except Exception as e:
        print("Error occurred while generating alerts:")
        import traceback
        traceback.print_exc()
