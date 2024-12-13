from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    is_admin: bool = False

class UserResponse(UserBase):
    id: int
    is_admin: bool
    session_id: str

    class Config:
        orm_mode = True

class SessionInfo(BaseModel):
    id: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime

    class Config:
        orm_mode = True 