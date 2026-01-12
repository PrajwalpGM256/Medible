import os
from app import create_app

# Get config from environment or default to development
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    print("\n🍽️  Medible - Med + Edible")
    print("=" * 40)
    print("Server starting on http://localhost:5000")
    print("=" * 40 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=(config_name == 'development'))