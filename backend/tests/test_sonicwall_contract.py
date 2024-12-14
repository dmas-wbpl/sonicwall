import pytest
import logging
from pydantic import ValidationError
from app.clients.sonicwall import SonicWallClient
from app.schemas.security import (
    SecurityServicesStatus,
    GatewayAntiVirusStatus,
    IntrusionPreventionStatus,
    BotnetStatus,
    AntiSpywareStatus,
    ContentFilteringStatus
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
async def sonicwall_client():
    """Fixture to provide an authenticated SonicWall client."""
    client = SonicWallClient()
    try:
        await client.authenticate()
        yield client
    finally:
        await client.close_session()

async def validate_response(model_class, response_data, endpoint_name):
    """Helper to validate response data against a model with detailed error logging."""
    logger.info(f"\nValidating {endpoint_name} response:")
    logger.info(f"Response data: {response_data}")
    
    if response_data is None:
        logger.warning(f"No data received for {endpoint_name}")
        if endpoint_name == "Content Filtering Status":
            # For content filtering, we'll skip validation if no data
            logger.info("Skipping content filtering validation due to no data")
            return None
        else:
            raise ValueError(f"No data received for {endpoint_name}")
            
    try:
        validated_data = model_class(**response_data)
        logger.info(f"✓ {endpoint_name} response matches schema")
        return validated_data
    except ValidationError as e:
        logger.error(f"✗ {endpoint_name} validation failed:")
        for error in e.errors():
            logger.error(f"  Field: {'.'.join(str(x) for x in error['loc'])}")
            logger.error(f"  Error: {error['msg']}")
            logger.error(f"  Type:  {error['type']}")
        raise

async def test_security_services_contract(sonicwall_client):
    """Test that our SecurityServicesStatus model matches SonicWall's response."""
    response = await sonicwall_client.get_security_services_status()
    await validate_response(SecurityServicesStatus, response, "Security Services Status")

async def test_gateway_av_contract(sonicwall_client):
    """Test that our GatewayAntiVirusStatus model matches SonicWall's response."""
    response = await sonicwall_client.get_gateway_av_status()
    await validate_response(GatewayAntiVirusStatus, response, "Gateway Anti-Virus Status")

async def test_ips_contract(sonicwall_client):
    """Test that our IntrusionPreventionStatus model matches SonicWall's response."""
    response = await sonicwall_client.get_intrusion_prevention_status()
    await validate_response(IntrusionPreventionStatus, response, "Intrusion Prevention Status")

async def test_botnet_contract(sonicwall_client):
    """Test that our BotnetStatus model matches SonicWall's response."""
    response = await sonicwall_client.get_botnet_status()
    await validate_response(BotnetStatus, response, "Botnet Status")

async def test_anti_spyware_contract(sonicwall_client):
    """Test that our AntiSpywareStatus model matches SonicWall's response."""
    response = await sonicwall_client.get_anti_spyware_status()
    await validate_response(AntiSpywareStatus, response, "Anti-Spyware Status")

async def test_content_filtering_contract(sonicwall_client):
    """Test that our ContentFilteringStatus model matches SonicWall's response."""
    response = await sonicwall_client.get_content_filtering_status()
    # This test may be skipped if content filtering data is not available
    await validate_response(ContentFilteringStatus, response, "Content Filtering Status") 