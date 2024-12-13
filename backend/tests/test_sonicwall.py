import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from app.clients.sonicwall import SonicWallClient

async def test_authentication():
    client = SonicWallClient()
    
    print("Testing SonicWall Authentication Flow")
    print("====================================")
    
    # Step 1: Authenticate
    print("\n1. Attempting authentication...")
    auth_success = await client.authenticate()
    print(f"Authentication {'successful' if auth_success else 'failed'}")
    
    if auth_success:
        # Step 2: Test getting security services status
        print("\n2. Fetching security services status...")
        status = await client.get_security_services_status()
        if status:
            print("Security services status retrieved successfully:")
            print(status)
        else:
            print("Failed to get security services status")
        
        # Step 3: Close session
        print("\n3. Closing session...")
        logout_success = await client.close_session()
        print(f"Session closure {'successful' if logout_success else 'failed'}")

def test_sonicwall_auth():
    """Pytest function for running the authentication test."""
    asyncio.run(test_authentication())
    
if __name__ == "__main__":
    asyncio.run(test_authentication()) 