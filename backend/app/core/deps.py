from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from app.clients.sonicwall import SonicWallClient

async def check_auth(request: Request):
    """Check if request has valid authentication."""
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Digest"}
        )

async def get_sonicwall_client() -> AsyncGenerator[SonicWallClient, None]:
    """Get an authenticated SonicWall client."""
    client = SonicWallClient()
    try:
        auth_success = await client.authenticate()
        if not auth_success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
        yield client
    finally:
        await client.close_session() 