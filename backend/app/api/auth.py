from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPDigest, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.security import verify_digest_auth, generate_digest_challenge
from app.services import user_service
from app.schemas.user import UserResponse

router = APIRouter(prefix="/api/sonicos/auth", tags=["auth"])
security = HTTPDigest()

@router.post("/", response_model=UserResponse)
async def login(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Login endpoint using RFC-7616 HTTP Digest Access Authentication.
    """
    if not credentials:
        response = Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": generate_digest_challenge()}
        )
        return response

    user = verify_digest_auth(credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators are allowed"
        )

    # Check if another admin is already logged in
    if user_service.is_another_admin_logged_in(db, user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Another administrator is currently logged in"
        )

    # Create session
    session = user_service.create_session(db, user.id)
    return UserResponse(
        id=user.id,
        username=user.username,
        is_admin=user.is_admin,
        session_id=session.id
    )

@router.delete("/")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Logout endpoint to terminate the current session.
    """
    user = verify_digest_auth(credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user_service.terminate_session(db, user.id)
    return {"detail": "Successfully logged out"} 