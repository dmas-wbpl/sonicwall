import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from tests.test_sonicwall import test_authentication
import asyncio

if __name__ == "__main__":
    print("Running SonicWall API Test")
    asyncio.run(test_authentication()) 