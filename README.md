# Multi-User Smart Home System

A comprehensive smart home system that supports multiple users managing multiple homes with real-time device control and updates.

## Features

- **Multi-user Support**: Secure user authentication and authorization
- **Multiple Homes**: Users can manage multiple homes with unique configurations
- **Room Management**: Organize devices by rooms within each home
- **Device Control**: Control various smart devices including:
  - Lights (on/off, brightness, color)
  - Locks (lock/unlock)
  - Alarms (arm/disarm)
  - Blinds (position control)
- **Real-time Updates**: Instant device status updates across all connected users
- **Responsive UI**: Modern, mobile-friendly interface

## Prerequisites

- Python 3.8 or higher
- SQLite3
- Modern web browser

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd smart-home-system
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python -c "from backend.database import engine; from backend.models import Base; Base.metadata.create_all(bind=engine)"
```

## Running the Application

1. Start the backend server:
```bash
uvicorn backend.main:app --reload
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

## Project Structure

```
smart-home-system/
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and endpoints
│   ├── models.py        # Database models
│   ├── auth.py          # Authentication system
│   ├── database.py      # Database configuration
│   └── websocket.py     # WebSocket server for real-time updates
├── frontend/
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   └── home.html        # Main application interface
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## API Endpoints

### Authentication
- `POST /token` - Login and get access token
- `POST /users/` - Register new user

### Homes
- `GET /homes/` - List user's homes
- `POST /homes/` - Create new home

### Rooms
- `GET /rooms/{home_id}` - List rooms in a home
- `POST /rooms/` - Create new room

### Devices
- `GET /devices/{room_id}` - List devices in a room
- `POST /devices/` - Create new device
- `PATCH /devices/{device_id}` - Update device status

### WebSocket
- `ws://localhost:8000/ws/{home_id}` - Real-time device updates

## Security

- JWT-based authentication
- Password hashing using bcrypt
- Secure WebSocket connections
- CORS protection
- Input validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 