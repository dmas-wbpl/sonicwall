import os
import sys
import asyncio
from typing import Dict, Any

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.clients.sonicwall import SonicWallClient

async def test_security_endpoints():
    """Test all security-related endpoints."""
    client = SonicWallClient()
    
    print("\nStarting security endpoints test...")
    
    # First authenticate
    print("\n1. Authenticating...")
    auth_result = await client.authenticate()
    if not auth_result:
        print("❌ Authentication failed! Cannot proceed with tests.")
        return
    print("✅ Authentication successful!")

    try:
        # Test Security Services Status
        print("\n2. Testing Security Services Status...")
        services_status = await client.get_security_services_status()
        if services_status:
            print("✅ Security Services Status retrieved successfully:")
            print("Response:", services_status)
            # Validate required fields
            assert "nodes_users" in services_status
            assert "gateway_anti_virus" in services_status
            assert "intrusion_prevention" in services_status
        else:
            print("❌ Failed to get Security Services Status")

        # Test Gateway AV Status
        print("\n3. Testing Gateway Anti-Virus Status...")
        av_status = await client.get_gateway_av_status()
        if av_status:
            print("✅ Gateway AV Status retrieved successfully:")
            print("Response:", av_status)
            # Validate required fields
            assert "signature_database" in av_status
            assert "gateway_anti_virus_expiration_date" in av_status
        else:
            print("❌ Failed to get Gateway AV Status")

        # Test IPS Status
        print("\n4. Testing Intrusion Prevention Status...")
        ips_status = await client.get_intrusion_prevention_status()
        if ips_status:
            print("✅ IPS Status retrieved successfully:")
            print("Response:", ips_status)
            # Validate required fields
            assert "signature_database" in ips_status
            assert "ips_service_expiration_date" in ips_status
        else:
            print("❌ Failed to get IPS Status")

        # Test Botnet Status
        print("\n5. Testing Botnet Filter Status...")
        botnet_status = await client.get_botnet_status()
        if botnet_status:
            print("✅ Botnet Status retrieved successfully:")
            print("Response:", botnet_status)
            # Validate required fields
            assert "botnet_database" in botnet_status
            assert "message" in botnet_status
        else:
            print("❌ Failed to get Botnet Status")

        # Test Anti-Spyware Status
        print("\n6. Testing Anti-Spyware Status...")
        spyware_status = await client.get_anti_spyware_status()
        if spyware_status:
            print("✅ Anti-Spyware Status retrieved successfully:")
            print("Response:", spyware_status)
            # Validate required fields
            assert "signature_database" in spyware_status
            assert "anti_spyware_expiration_date" in spyware_status
        else:
            print("❌ Failed to get Anti-Spyware Status")

        # Test Content Filtering Status
        print("\n7. Testing Content Filtering Status...")
        content_status = await client.get_content_filtering_status()
        if content_status:
            print("✅ Content Filtering Status retrieved successfully:")
            print("Response:", content_status)
            # Validate required fields
            assert "database_version" in content_status
            assert "categories" in content_status
        else:
            print("❌ Failed to get Content Filtering Status")

    except AssertionError as e:
        print(f"\n❌ Validation error: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
    
    finally:
        # Always try to close the session
        print("\n8. Closing session...")
        if await client.close_session():
            print("✅ Session closed successfully")
        else:
            print("❌ Failed to close session")

if __name__ == "__main__":
    asyncio.run(test_security_endpoints()) 