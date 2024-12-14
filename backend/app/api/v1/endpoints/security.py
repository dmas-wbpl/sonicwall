from fastapi import APIRouter, Depends
from app.clients.sonicwall import SonicWallClient
from app.core.deps import get_sonicwall_client, check_auth
from app.schemas.security import (
    SecurityServicesStatus,
    GatewayAntiVirusStatus,
    IntrusionPreventionStatus,
    BotnetStatus,
    AntiSpywareStatus,
    ContentFilteringStatus
)

router = APIRouter(
    prefix="/security",
    tags=["security"],
    dependencies=[Depends(check_auth)]
)

@router.get("/services/status", response_model=SecurityServicesStatus)
async def get_security_services_status(
    client: SonicWallClient = Depends(get_sonicwall_client)
):
    """Get the status of all security services."""
    return await client.get_security_services_status()

@router.get("/gateway-av/status", response_model=GatewayAntiVirusStatus)
async def get_gateway_av_status(
    client: SonicWallClient = Depends(get_sonicwall_client)
):
    """Get Gateway Anti-Virus status."""
    return await client.get_gateway_av_status()

@router.get("/ips/status", response_model=IntrusionPreventionStatus)
async def get_intrusion_prevention_status(
    client: SonicWallClient = Depends(get_sonicwall_client)
):
    """Get Intrusion Prevention status."""
    return await client.get_intrusion_prevention_status()

@router.get("/botnet/status", response_model=BotnetStatus)
async def get_botnet_status(
    client: SonicWallClient = Depends(get_sonicwall_client)
):
    """Get Botnet Filter status."""
    return await client.get_botnet_status()

@router.get("/anti-spyware/status", response_model=AntiSpywareStatus)
async def get_anti_spyware_status(
    client: SonicWallClient = Depends(get_sonicwall_client)
):
    """Get Anti-Spyware status."""
    return await client.get_anti_spyware_status()

@router.get("/content-filtering/status", response_model=ContentFilteringStatus)
async def get_content_filtering_status(
    client: SonicWallClient = Depends(get_sonicwall_client)
):
    """Get Content Filtering status."""
    return await client.get_content_filtering_status() 