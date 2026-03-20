from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from typing import Optional
from database import get_connection
from schemas import *
from utils import hash_password, verify_password
from auth import create_token, decode_token
from fastapi import HTTPException
app = FastAPI()
security = HTTPBearer()


# ================= AUTH ================= #

@app.post("/register")
def register(user: UserRegister):
    
    # Manual validation
    if not user.email or user.email.strip() == "":
        raise HTTPException(status_code=400, detail="Email is required")

    if not user.password or user.password.strip() == "":
        raise HTTPException(status_code=400, detail="Password is required")
    if "@" not in user.email:
        raise HTTPException(status_code=400, detail="Invalid email format")

    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=%s", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already exists")

    cursor.execute(
        "INSERT INTO users (email, password) VALUES (%s, %s)",
        (user.email, hash_password(user.password))
    )
    conn.commit()

    return {"message": "Registered successfully"}
@app.post("/login")
def login(user: UserLogin):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s", (user.email,))
    db_user = cursor.fetchone()

    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_token({"user_id": db_user["id"]})
    return {"access_token": token}


# ================= AUTH CHECK ================= #

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload["user_id"]


# ================= EVENTS ================= #

@app.post("/events")
def create_event(event: EventCreate, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO events (user_id, title, description, event_time) VALUES (%s, %s, %s, %s)",
        (user_id, event.title, event.description, event.event_time)
    )
    conn.commit()

    return {"message": "Event created"}


@app.get("/events")
def get_events(
    status: Optional[str] = None,
    time_filter: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "event_time",
    order: Optional[str] = "asc",
    page: int = 1,
    limit: int = 5,
    user_id: int = Depends(get_current_user)
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM events WHERE user_id=%s"
    params = [user_id]

    #  STATUS FILTER
    if status:
        if status not in ["pending", "done", "cancelled"]:
            raise HTTPException(400, "Invalid status")
        query += " AND status=%s"
        params.append(status)

    #  TIME FILTER
    if time_filter:
        now = datetime.now()
        if time_filter == "upcoming":
            query += " AND event_time > %s"
            params.append(now)
        elif time_filter == "past":
            query += " AND event_time < %s"
            params.append(now)
        else:
            raise HTTPException(400, "Invalid time filter")

    #  SEARCH
    if search:
        query += " AND (title LIKE %s OR description LIKE %s)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    #  SORTING
    allowed_sort_fields = ["event_time", "created_at", "status"]
    if sort_by not in allowed_sort_fields:
        raise HTTPException(400, "Invalid sort field")

    if order not in ["asc", "desc"]:
        raise HTTPException(400, "Invalid order")

    query += f" ORDER BY {sort_by} {order}"

    #  PAGINATION
    offset = (page - 1) * limit
    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(query, tuple(params))
    return cursor.fetchall()

@app.put("/events/{event_id}")
def update_event(event_id: int, event: EventUpdate, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events WHERE id=%s AND user_id=%s", (event_id, user_id))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Not found")

    cursor.execute(
        "UPDATE events SET title=%s, description=%s, event_time=%s WHERE id=%s",
        (event.title, event.description, event.event_time, event_id)
    )
    conn.commit()

    return {"message": "Event updated"}


@app.delete("/events/{event_id}")
def delete_event(event_id: int, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM events WHERE id=%s AND user_id=%s", (event_id, user_id))
    conn.commit()

    return {"message": "Event deleted"}


# ================= REMINDERS ================= #

@app.post("/reminders")
def create_reminder(rem: ReminderCreate, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO reminders (user_id, title, reminder_time) VALUES (%s, %s, %s)",
        (user_id, rem.title, rem.reminder_time)
    )
    conn.commit()

    return {"message": "Reminder created"}


@app.get("/reminders")
def get_reminders(
    status: Optional[str] = None,
    time_filter: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "reminder_time",
    order: Optional[str] = "asc",
    page: int = 1,
    limit: int = 5,
    user_id: int = Depends(get_current_user)
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM reminders WHERE user_id=%s"
    params = [user_id]

    if status:
        if status not in ["pending", "done", "cancelled"]:
            raise HTTPException(400, "Invalid status")
        query += " AND status=%s"
        params.append(status)

    if time_filter:
        now = datetime.now()
        if time_filter == "upcoming":
            query += " AND reminder_time > %s"
            params.append(now)
        elif time_filter == "past":
            query += " AND reminder_time < %s"
            params.append(now)
        else:
            raise HTTPException(400, "Invalid time filter")

    if search:
        query += " AND title LIKE %s"
        params.append(f"%{search}%")

    allowed_sort_fields = ["reminder_time", "created_at", "status"]
    if sort_by not in allowed_sort_fields:
        raise HTTPException(400, "Invalid sort field")

    if order not in ["asc", "desc"]:
        raise HTTPException(400, "Invalid order")

    query += f" ORDER BY {sort_by} {order}"

    offset = (page - 1) * limit
    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(query, tuple(params))
    return cursor.fetchall()

@app.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM reminders WHERE id=%s AND user_id=%s", (reminder_id, user_id))
    conn.commit()

    return {"message": "Reminder deleted"}

@app.put("/events/{event_id}/status")
def update_event_status(event_id: int, status: str, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # get event
    cursor.execute("SELECT * FROM events WHERE id=%s AND user_id=%s", (event_id, user_id))
    event = cursor.fetchone()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    current_status = event["status"]

    #  prevent invalid transitions
    if current_status == "done":
        raise HTTPException(status_code=400, detail="Already completed")

    if current_status == "cancelled":
        raise HTTPException(status_code=400, detail="Already cancelled")

    if status not in ["done", "pending", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    # update
    cursor.execute(
        "UPDATE events SET status=%s WHERE id=%s",
        (status, event_id)
    )
    conn.commit()

    return {"message": f"Event marked as {status}"}

@app.put("/reminders/{reminder_id}/status")
def update_reminder_status(reminder_id: int, status: str, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reminders WHERE id=%s AND user_id=%s", (reminder_id, user_id))
    reminder = cursor.fetchone()

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    current_status = reminder["status"]

    if current_status == "done":
        raise HTTPException(status_code=400, detail="Already completed")

    if current_status == "cancelled":
        raise HTTPException(status_code=400, detail="Already cancelled")

    if status not in ["done", "pending", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    cursor.execute(
        "UPDATE reminders SET status=%s WHERE id=%s",
        (status, reminder_id)
    )
    conn.commit()

    return {"message": f"Reminder marked as {status}"}