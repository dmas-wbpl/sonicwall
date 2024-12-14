from typing import Optional, Any
from pydantic import BaseModel

class SecurityServicesStatus(BaseModel):
    nodes_users: str
    ssl_vpn_nodes_users: str
    virtual_assist_nodes_users: str
    vpn: str
    global_vpn_client: str
    cfs_content_filter_: str
    expanded_feature_set: str
    endpoint_security: str
    gateway_anti_virus: str
    capture_atp: str
    anti_spyware: str
    intrusion_prevention: str
    app_control: str
    app_visualization: str
    anti_spam: str
    analyzer: str
    dpi_ssl: str
    dpi_ssh: str
    wan_acceleration: str
    wxac_acceleration: str
    botnet: str
    dns_filtering: str

class GatewayAntiVirusStatus(BaseModel):
    signature_database: str
    signature_database_timestamp: str
    last_checked: str
    gateway_anti_virus_expiration_date: str

class IntrusionPreventionStatus(BaseModel):
    signature_database: str
    signature_database_timestamp: str
    last_checked: str
    ips_service_expiration_date: str

class BotnetStatus(BaseModel):
    botnet_database: str
    message: str

class AntiSpywareStatus(BaseModel):
    signature_database: str
    signature_database_timestamp: str
    last_checked: str
    anti_spyware_expiration_date: str
    active_signatures: Optional[int] = None
    blocked_today: Optional[int] = None

class ContentFilteringCategory(BaseModel):
    id: int
    name: str
    status: str
    hits_today: Optional[int] = None

class ContentFilteringStatus(BaseModel):
    database_version: Optional[str] = None
    last_updated: Optional[str] = None
    expiration_date: Optional[str] = None
    total_requests_today: Optional[int] = None
    total_blocked_today: Optional[int] = None
    categories: Optional[list[ContentFilteringCategory]] = None
    extra: Optional[dict[str, Any]] = None