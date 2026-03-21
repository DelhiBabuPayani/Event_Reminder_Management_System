# Event & Reminder Management System (Backend API)

##  Overview
This project is a Python-based backend API for managing events and reminders. It enables users to securely register, authenticate, and manage their personal events with features like lifecycle tracking, filtering, and validation.

---

## Features
- User Authentication (JWT-based login system)
- Create, Update, Delete Events & Reminders
- Event Status Management (Pending / Done / Cancelled)
- Filtering & Search
- Input validation and structured error handling

---

##  Tech Stack
- Python
- FastAPI
- SQLite (default DB)
- SQLAlchemy (ORM)
- JWT Authentication

---

## Project Structure

```
EVENT_REMINDER_PROJECT/
│
├── __pycache__/        # Compiled Python files
├── .dist/              # Build distribution files
├── .venv/              # Virtual environment
├── .python-version     # Python version config
│
├── auth.py             # Authentication logic (JWT)
├── database.py         # Database connection setup
├── main.py             # Entry point of the application
├── models.py           # Database models
├── schemas.py          # Request/response validation schemas
├── utils.py            # Utility/helper functions
│
├── pyproject.toml      # Project configuration
├── requirements.txt    # Dependencies
├── uv.lock             # Dependency lock file
└── README.md           # Project documentation
```

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

---

### Installation

```bash
git clone https://github.com/DelhiBabuPayani/Event_Reminder_Management_System.git
cd event-reminder-project
```

---

### Create Virtual Environment

python -m venv .venv

Activate it:

.venv\Scripts\activate

### Install Dependencies

pip install -r requirements.txt

### Run the Application

uvicorn main:app --reload

## Authentication Flow

1. Register user  
2. Login to receive JWT token  
3. Use token in headers:

Authorization: Bearer <your_token>


## Development Decisions

### 1. FastAPI Framework
Chosen for:
- High performance
- Built-in validation using Pydantic
- Automatic API documentation (Swagger)

---

### 2. JWT Authentication
Used because:
- Stateless authentication
- Scalable and secure
- No server-side session management required

---

### 3. Modular File Design
Files are separated by responsibility:
- `main.py` → App entry point
- `schemas.py` → Validation
- `auth.py` → Authentication logic
- `database.py` → DB setup
- `utils.py` → Helper functions

This improves maintainability and scalability.

---

### 4. Database Design
- Structured using SQLAlchemy ORM
- Separation of models and schemas ensures clean architecture
---

### 5. Validation & Error Handling
- Implemented using Pydantic schemas
- Ensures clean and valid input data
- Provides consistent error responses

---

## Sample API Endpoints

| Method | Endpoint | Description |
|--------|---------|------------|
| POST | /register | Register user |
| POST | /login | Login user |
| GET | /events | Get events |
| POST | /events | Create event |
| PUT | /events/{id} | Update event |
| DELETE | /events/{id} | Delete event |

# Event_Reminder_Management_Systems