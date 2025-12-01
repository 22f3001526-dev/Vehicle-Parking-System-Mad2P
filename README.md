# Vehicle Parking App - MAD-II Project

A comprehensive multi-user vehicle parking management system for 4-wheeler parking.

## Technology Stack

### Backend
- **Flask** - REST API framework
- **SQLite** - Database
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - Authentication
- **Redis** - Caching and message broker
- **Celery** - Background jobs and scheduled tasks

### Frontend
- **VueJS 3** - Progressive JavaScript framework
- **Vue Router** - Client-side routing
- **Bootstrap 5** - UI styling
- **Chart.js** - Data visualization
- **Axios** - HTTP client

## Features

### Admin Features
- Create, edit, and delete parking lots
- Auto-generate parking spots based on lot capacity
- View all parking spots and their status
- View all registered users
- View analytics and revenue reports
- Monitor parking lot occupancy

### User Features
- Register and login
- View available parking lots
- Auto-allocation of parking spots
- Occupy and release parking spots
- View parking history and costs
- View personal analytics
- Export parking history as CSV

### Automated Features
- Daily reminders for inactive users
- Monthly activity reports via email
- Async CSV export generation
- Real-time cache updates

## Project Structure

```
vehicle_parking_app/
├── backend/
│   ├── app.py              # Flask application
│   ├── config.py           # Configuration
│   ├── init_db.py          # Database initialization
│   ├── models/             # Database models
│   ├── routes/             # API routes
│   ├── tasks/              # Celery tasks
│   └── utils/              # Utility functions
├── frontend/
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── router/         # Vue Router config
│   │   └── services/       # API services
│   └── public/
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- Redis Server

### Backend Setup

1. Create virtual environment:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize database:
```bash
python init_db.py
```

4. Run Flask server:
```bash
python app.py
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run development server:
```bash
npm run dev
```

### Redis Setup

Start Redis server:
```bash
redis-server
```

### Celery Setup

1. Start Celery worker:
```bash
cd backend
celery -A tasks.celery_config worker --loglevel=info
```

2. Start Celery beat (scheduler):
```bash
celery -A tasks.celery_config beat --loglevel=info
```

## Default Admin Credentials
- **Username**: admin
- **Password**: admin123

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Admin Routes
- `GET /api/admin/lots` - Get all parking lots
- `POST /api/admin/lots` - Create parking lot
- `PUT /api/admin/lots/<id>` - Update parking lot
- `DELETE /api/admin/lots/<id>` - Delete parking lot
- `GET /api/admin/spots` - Get all parking spots
- `GET /api/admin/users` - Get all users

### User Routes
- `GET /api/user/lots/available` - Get available lots
- `POST /api/user/reserve` - Reserve a spot
- `POST /api/user/occupy/<id>` - Occupy a spot
- `POST /api/user/release/<id>` - Release a spot
- `GET /api/user/reservations` - Get reservation history

## Milestone Progress

- [x] Milestone 0: GitHub Repository Setup (5%)
- [ ] Milestone 1: Database Models and Schema Setup (15%)
- [ ] Milestone 2: Authentication & Role-based Access (10%)
- [ ] Milestone 3: Admin Dashboard and Management (20%)
- [ ] Milestone 4: User Dashboard and Reservation System (15%)
- [ ] Milestone 5: Reservation History and Cost Calculation (10%)
- [ ] Milestone 6: Charts and Analytics (10%)
- [ ] Milestone 7: Redis Caching (5%)
- [ ] Milestone 8: Backend Jobs - Celery (10%)

## License
Academic Project - MAD-II Course
