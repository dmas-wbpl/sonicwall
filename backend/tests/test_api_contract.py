import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    """Create a test client fixture."""
    with TestClient(app) as test_client:
        yield test_client

def test_api_docs_endpoints(client):
    """Test that API documentation endpoints are accessible."""
    # OpenAPI JSON
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()
    
    # Swagger UI
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()
    
    # ReDoc
    response = client.get("/api/redoc")
    assert response.status_code == 200
    assert "redoc" in response.text.lower()

def test_api_version_prefix(client):
    """Test that all endpoints use the correct version prefix."""
    openapi = client.get("/api/openapi.json").json()
    paths = openapi.get("paths", {})
    
    # Check all paths start with /api/v1
    for path in paths:
        assert path.startswith("/api/v1/"), f"Path {path} does not start with /api/v1/"

def test_security_endpoints_schema(client):
    """Test that security endpoints have correct response schemas."""
    openapi = client.get("/api/openapi.json").json()
    paths = openapi.get("paths", {})
    schemas = openapi.get("components", {}).get("schemas", {})
    
    # Test all security endpoints exist
    endpoints = [
        "/api/v1/security/services/status",
        "/api/v1/security/gateway-av/status",
        "/api/v1/security/ips/status",
        "/api/v1/security/botnet/status",
        "/api/v1/security/anti-spyware/status",
        "/api/v1/security/content-filtering/status"
    ]
    
    for endpoint in endpoints:
        assert endpoint in paths, f"Endpoint {endpoint} not found"
        assert "get" in paths[endpoint], f"GET method not found for {endpoint}"
        
        # Check response schema exists
        response_schema = paths[endpoint]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
        assert "$ref" in response_schema, f"Response schema reference not found for {endpoint}"
    
    # Test all schemas exist
    required_schemas = [
        "SecurityServicesStatus",
        "GatewayAntiVirusStatus",
        "IntrusionPreventionStatus",
        "BotnetStatus",
        "AntiSpywareStatus",
        "ContentFilteringStatus",
        "ContentFilteringCategory"  # Sub-schema for ContentFilteringStatus
    ]
    
    for schema in required_schemas:
        assert schema in schemas, f"Schema {schema} not found in OpenAPI spec"

def test_error_responses(client):
    """Test that endpoints return proper error responses."""
    # Test unauthorized access
    response = client.get("/api/v1/security/services/status")
    assert response.status_code == 401
    assert "detail" in response.json()
    
    # Test not found
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_response_models(client):
    """Test that response models have required fields."""
    openapi = client.get("/api/openapi.json").json()
    schemas = openapi.get("components", {}).get("schemas", {})
    
    # SecurityServicesStatus required fields
    security_services = schemas["SecurityServicesStatus"]["properties"]
    assert all(field in security_services for field in [
        "nodes_users", "ssl_vpn_nodes_users", "gateway_anti_virus", "anti_spyware",
        "intrusion_prevention", "botnet"
    ])
    
    # Anti-Spyware required fields
    anti_spyware = schemas["AntiSpywareStatus"]["properties"]
    assert all(field in anti_spyware for field in [
        "signature_database", "signature_database_timestamp", "last_checked",
        "anti_spyware_expiration_date", "active_signatures", "blocked_today"
    ])
    
    # Content Filtering required fields
    content_filtering = schemas["ContentFilteringStatus"]["properties"]
    assert all(field in content_filtering for field in [
        "database_version", "last_updated", "expiration_date",
        "total_requests_today", "total_blocked_today", "categories"
    ])

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 