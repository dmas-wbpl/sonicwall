# SonicWall Management API v1.0.0

## Overview
This API provides endpoints for managing SonicWall security appliances, focusing on security services status and configuration.

## Authentication
Uses RFC-7616 HTTP Digest Access Authentication. All requests must be authenticated.

### Authentication Flow
1. Request challenge: `GET /api/v1/auth`
2. Send credentials: `POST /api/v1/auth`
3. Start session: `POST /api/v1/start-management`
4. End session: `DELETE /api/v1/auth`

## Security Services Endpoints

### Get All Security Services Status
```http
GET /api/v1/security/services/status
```
Returns licensing status of all security services.

### Get Gateway Anti-Virus Status
```http
GET /api/v1/security/gateway-av/status
```
Returns Gateway Anti-Virus status including signature database information.

### Get Intrusion Prevention Status
```http
GET /api/v1/security/ips/status
```
Returns IPS status including signature database information.

### Get Botnet Filter Status
```http
GET /api/v1/security/botnet/status
```
Returns Botnet Filter status and database information.

### Get Anti-Spyware Status
```http
GET /api/v1/security/anti-spyware/status
```
Returns Anti-Spyware status including signature database and threat statistics.

### Get Content Filtering Status
```http
GET /api/v1/security/content-filtering/status
```
Returns Content Filtering status including database information and category statistics.

## Response Formats

### Security Services Status Response
```json
{
  "nodes_users": "Licensed - Unlimited Nodes",
  "ssl_vpn_nodes_users": "Licensed - 12 Nodes(0 in use)",
  "vpn": "Licensed",
  "gateway_anti_virus": "Licensed",
  // ... other services
}
```

### Gateway Anti-Virus Status Response
```json
{
  "signature_database": "Downloaded",
  "signature_database_timestamp": "UTC 12/12/2024 15:02:28.000",
  "last_checked": "12/13/2024 16:29:02.864",
  "gateway_anti_virus_expiration_date": "UTC 04/05/2026 00:00:00.000"
}
```

### Intrusion Prevention Status Response
```json
{
  "signature_database": "Downloaded",
  "signature_database_timestamp": "UTC 12/12/2024 14:53:13.000",
  "last_checked": "12/13/2024 16:29:02.864",
  "ips_service_expiration_date": "UTC 04/05/2026 00:00:00.000"
}
```

### Botnet Filter Status Response
```json
{
  "botnet_database": "Downloaded",
  "message": "Botnet Filter Available"
}
```

### Anti-Spyware Status Response
```json
{
  "signature_database": "Downloaded",
  "signature_database_timestamp": "UTC 12/12/2024 15:02:28.000",
  "last_checked": "12/13/2024 16:29:02.864",
  "anti_spyware_expiration_date": "UTC 04/05/2026 00:00:00.000",
  "active_signatures": 12500,
  "blocked_today": 42
}
```

### Content Filtering Status Response
```json
{
  "database_version": "20240112",
  "last_updated": "UTC 12/12/2024 15:02:28.000",
  "expiration_date": "UTC 04/05/2026 00:00:00.000",
  "total_requests_today": 15000,
  "total_blocked_today": 150,
  "categories": [
    {
      "id": 1,
      "name": "Adult Content",
      "status": "Blocked",
      "hits_today": 25
    },
    {
      "id": 2,
      "name": "Business",
      "status": "Allowed",
      "hits_today": 1250
    }
  ]
}
```

## Error Handling
All endpoints return standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a detail message:
```json
{
  "detail": "Error message here"
}
```

## Rate Limiting
- Maximum 100 requests per minute per IP
- Authentication endpoints: 10 requests per minute per IP

## CORS
Currently configured to allow all origins (*) for development. In production, specific origins should be configured.

## API Versioning
Current version: v1.0.0
API version is included in the URL path: `/api/v1/`

## Documentation
- OpenAPI/Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`
- OpenAPI JSON: `/api/openapi.json` 