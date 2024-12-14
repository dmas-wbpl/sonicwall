from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_sonicwall_client
from app.clients.sonicwall import SonicWallClient

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login")
async def login(client: SonicWallClient = Depends(get_sonicwall_client)):
    """
    Authenticate with the SonicWall device and start a management session.
    
    Returns:
        dict: Authentication success message
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        auth_success = await client.authenticate()
        if not auth_success:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed"
            )
        return {"message": "Successfully authenticated"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication error: {str(e)}"
        )

@router.delete("/logout")
async def logout(client: SonicWallClient = Depends(get_sonicwall_client)):
    """
    End the current management session.
    
    Returns:
        dict: Logout success message
        
    Raises:
        HTTPException: If session termination fails
    """
    try:
        logout_success = await client.close_session()
        if not logout_success:
            raise HTTPException(
                status_code=500,
                detail="Failed to terminate session"
            )
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Logout error: {str(e)}"
        ) 