# Medible

Check food-drug interactions before they become a problem.

Medible helps users manage their medications and quickly check whether specific foods might interfere with their prescriptions. Built for people who want straightforward answers without digging through medical journals.

---

## Tech Stack

**Backend**
- Python 3.11+ / Flask
- SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)
- Flask-JWT-Extended for auth
- OpenFDA API for drug data
- USDA FoodData Central API for nutrition info

**Frontend**
- Vue 3 with Composition API
- TypeScript
- Pinia for state management
- Tailwind CSS
- Vite

**Infrastructure**
- Docker & Docker Compose
- Gunicorn (production WSGI)

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings (or use defaults for local dev)

# Initialize database
flask db upgrade

# Run the server
python run.py
```

Backend runs at `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## Database

SQLite is used by default for local development. The database file is created automatically in `backend/instance/`.

To reset the database:
```bash
cd backend
rm instance/medible.db
flask db upgrade
```

For production, set `DATABASE_URL` in your environment to point to PostgreSQL.

---

## Seeding Demo Data

Populate the database with sample users and medications:

```bash
cd backend
python seed_data.py
```

This creates 5 demo accounts:

| Email | Password |
|-------|----------|
| demo@medible.com | Demo123! |
| john@example.com | John123! |
| sarah@example.com | Sarah123! |
| mike@example.com | Mike123! |
| emma@example.com | Emma123! |

Each account comes with pre-configured medications and search history.

---

## Docker

Run the entire stack with Docker Compose:

```bash
docker-compose up --build
```

---

## Project Structure

```
medible/
├── backend/
│   ├── app/
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic, external APIs
│   │   └── data/          # Static interaction data
│   ├── tests/
│   ├── seed_data.py       # Database seeder
│   └── run.py             # Entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Route views
│   │   ├── stores/        # Pinia state
│   │   └── services/      # API client
│   └── index.html
│
└── docker-compose.yml
```

---

## API Endpoints

All endpoints are prefixed with `/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Create account |
| POST | /auth/login | Get JWT token |
| GET | /drugs/search?q= | Search medications |
| GET | /foods/search?q= | Search foods |
| POST | /interactions/check | Check food-drug interaction |
| GET | /medications | List user's medications |
| POST | /medications | Add medication |
| DELETE | /medications/:id | Remove medication |

---

## Environment Variables

**Backend** (`backend/.env`)

```
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///medible.db
OPENFDA_API_KEY=optional
USDA_API_KEY=your-usda-key
```

**Frontend** (`frontend/.env`)

```
VITE_API_URL=http://localhost:5000/api/v1
```

---

## License

MIT
