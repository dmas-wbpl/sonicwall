from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.session import Session as SessionModel

SESSION_DURATION = timedelta(hours=1)  # Session expires after 1 hour

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def is_another_admin_logged_in(db: Session, current_user_id: int) -> bool:
    """Check if another admin user has an active session."""
    active_admin_sessions = (
        db.query(SessionModel)
        .join(User)
        .filter(User.is_admin == True)
        .filter(User.id != current_user_id)
        .filter(SessionModel.is_active == True)
        .filter(SessionModel.expires_at > datetime.utcnow())
        .first()
    )
    return active_admin_sessions is not None

def create_session(db: Session, user_id: int) -> SessionModel:
    """Create a new session for the user."""
    # First, deactivate any existing sessions for this user
    db.query(SessionModel).filter(
        SessionModel.user_id == user_id,
        SessionModel.is_active == True
    ).update({"is_active": False})

    # Create new session
    session = SessionModel(
        id=str(uuid.uuid4()),
        user_id=user_id,
        expires_at=datetime.utcnow() + SESSION_DURATION
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def terminate_session(db: Session, user_id: int) -> None:
    """Terminate all active sessions for the user."""
    db.query(SessionModel).filter(
        SessionModel.user_id == user_id,
        SessionModel.is_active == True
    ).update({"is_active": False})
    db.commit()

def validate_session(db: Session, session_id: str) -> bool:
    """Validate if a session is active and not expired."""
    session = (
        db.query(SessionModel)
        .filter(
            SessionModel.id == session_id,
            SessionModel.is_active == True,
            SessionModel.expires_at > datetime.utcnow()
        )
        .first()
    )
    return session is not None 