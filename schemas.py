from pydantic import BaseModel, EmailStr
from datetime import datetime

# AUTH
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# EVENTS
class EventCreate(BaseModel):
    title: str
    description: str
    event_time: datetime

class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    event_time: datetime | None = None


# REMINDERS
class ReminderCreate(BaseModel):
    title: str
    reminder_time: datetime

class ReminderUpdate(BaseModel):
    title: str | None = None
    reminder_time: datetime | None = None