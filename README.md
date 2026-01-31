# Agency Performance Tracker

A web application for tracking and managing agency performance metrics.

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

## Project Structure

```
agency-performance-tracker/
├── backend/          # FastAPI backend
│   ├── app/          # Application code
│   ├── scripts/      # Database initialization scripts
│   └── requirements.txt
├── frontend/         # React + Vite frontend
│   ├── src/
│   └── package.json
└── README.md
```

## Backend Setup

### 1. Navigate to backend directory

```bash
cd backend
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment

Copy the example environment file and adjust as needed:

```bash
cp .env.example .env
```

Environment variables:
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./agency_tracker.db` |
| `SECRET_KEY` | JWT secret key | Change in production |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |

### 6. Initialize database

```bash
python scripts/init_all.py
```

This will:
- Create all database tables
- Seed initial KPIs
- Seed countries for security questions
- Create default admin user

### 7. Run development server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Frontend Setup

### 1. Navigate to frontend directory

```bash
cd frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure environment

Copy the example environment file:

```bash
cp .env.example .env
```

Environment variables:
| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000/api` |

### 4. Run development server

```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## Running Both Services

Open two terminals:

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate on macOS/Linux
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Default Credentials

After running `init_all.py`, an admin user is created:

- **Username:** admin
- **Password:** admin

> Change the password after first login in production.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/auth/*` | Authentication (login, refresh, etc.) |
| `/api/users/*` | User management |
| `/api/agencies/*` | Agency CRUD |
| `/api/kpis/*` | KPI definitions |
| `/api/targets/*` | Performance targets |
| `/api/results/*` | Monthly results |
| `/api/reviews/*` | Monthly reviews |
| `/api/dashboard/*` | Dashboard data |
| `/api/countries/*` | Security countries |

## Available Scripts

### Backend

```bash
python scripts/init_all.py    # Initialize database with seed data
```

### Frontend

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite (dev) / PostgreSQL (prod)

### Frontend
- React 18
- TypeScript
- Vite
- React Router
- TanStack Query
- i18next
