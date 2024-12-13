# SonicWall API Integration Guide

## Authentication Flow

1. **Initial Challenge Request**
   ```http
   GET https://{SONICWALL_IP}/api/sonicos/auth
   ```
   - Expect 401 response with WWW-Authenticate header
   - Parse digest authentication parameters from header

2. **Authentication Response**
   ```http
   POST https://{SONICWALL_IP}/api/sonicos/auth
   Headers:
     Authorization: Digest {auth_string}
     Content-Type: application/json
     Accept: application/json
   ```
   - Calculate digest response using:
     - username
     - realm (from challenge)
     - nonce (from challenge)
     - uri: "/api/sonicos/auth"
     - qop (from challenge)
     - nc: "00000001"
     - cnonce: generated UUID
     - algorithm: SHA-256

3. **Start Management Session**
   ```http
   POST https://{SONICWALL_IP}/api/sonicos/start-management
   Headers: {same as auth response}
   ```
   - Required after successful authentication
   - Must be called before accessing any other endpoints

## Required Endpoints

### Threat Detection & Prevention

1. **Intrusion Prevention Status**
   ```http
   GET /api/sonicos/reporting/intrusion-prevention
   Response: {
     "signature_database": "Downloaded",
     "signature_database_timestamp": "UTC timestamp",
     "last_checked": "timestamp",
     "ips_service_expiration_date": "UTC timestamp"
   }
   ```

2. **Gateway Antivirus Status**
   ```http
   GET /api/sonicos/reporting/gateway-antivirus
   Response: {
     "signature_database": "Downloaded",
     "signature_database_timestamp": "UTC timestamp",
     "last_checked": "timestamp",
     "gateway_anti_virus_expiration_date": "UTC timestamp"
   }
   ```

3. **Botnet Status**
   ```http
   GET /api/sonicos/reporting/botnet/status
   Response: {
     "botnet_database": "Downloaded",
     "message": "Botnet Filter Available"
   }
   ```

4. **Geo-IP Status**
   ```http
   GET /api/sonicos/reporting/geo-ip/status
   Response: {
     "country_database": "Downloaded",
     "message": "Geo Enforcement Available"
   }
   ```

### User Security

1. **Active Users**
   ```http
   GET /api/sonicos/user/status/active
   Response: [
     {
       "name": "username",
       "ip_address": "ip",
       "ip_addresses": ["ip1", "ip2"],
       "client_public_ip": "ip",
       "status": "status",
       "privileges": "privileges",
       "session_time": "duration",
       "time_remaining": "duration"
     }
   ]
   ```

2. **User Statistics**
   ```http
   GET /api/sonicos/reporting/user/statistics
   Response: [
     {
       "user_type": "type",
       "active": number,
       "inactive": number,
       "total": number
     }
   ]
   ```

### System Security

1. **Security Services Status**
   ```http
   GET /api/sonicos/reporting/status/security-services
   Response: {
     "nodes_users": "Licensed - Unlimited Nodes",
     "ssl_vpn_nodes_users": "Licensed - X Nodes(Y in use)",
     "gateway_anti_virus": "Licensed",
     "intrusion_prevention": "Licensed",
     "app_control": "Licensed",
     ...
   }
   ```

2. **Firewall Connection Status**
   ```http
   GET /api/sonicos/reporting/firewall/connection-status
   Response: [
     {
       "appflow": boolean,
       "external_collector": boolean,
       "maximum_spi_connections": "number",
       "maximum_dpi_connections": "number",
       "dpi_connections": "number"
     }
   ]
   ```

## Optional Endpoints

These endpoints may not be available in all configurations:

1. **Logged-In Users**
   ```http
   GET /api/sonicos/user/status/logged-in
   ```

2. **Security Policies Statistics**
   ```http
   GET /api/sonicos/reporting/security-policies/statistics
   ```

## Environment Variables Required

```env
SONICWALL_IP=<firewall_ip>
SONICWALL_API_USERNAME=<api_username>
SONICWALL_API_PASSWORD=<api_password>
```

## Common Headers

All API requests should include:
```http
Accept: application/json
Content-Type: application/json
```

## Error Handling

1. Authentication Errors:
   - 401: Unauthorized - Re-authenticate
   - 403: Forbidden - Check credentials

2. Session Errors:
   - 400: Bad Request - Check if management session is active
   - 404: Not Found - Endpoint not available in current configuration

3. Data Errors:
   - 500: Internal Server Error - Retry with exponential backoff
   - 503: Service Unavailable - Firewall may be busy

## Best Practices

1. **Session Management**
   - Keep track of authentication state
   - Re-authenticate on 401 responses
   - Close management session when done

2. **Error Handling**
   - Implement retry logic with backoff
   - Log detailed error responses
   - Handle SSL/TLS verification appropriately

3. **Data Collection**
   - Cache responses where appropriate
   - Implement rate limiting
   - Use appropriate timeouts

4. **Security**
   - Store credentials securely
   - Use environment variables
   - Never disable SSL verification in production

## Testing

Use the provided test suite in `backend/tests/test_sonicwall.py` to verify:
1. Authentication flow
2. Endpoint accessibility
3. Response data structures
4. Error handling

Run tests with:
```bash
python -m pytest tests/test_sonicwall.py -v
```

## Log Collection

1. **Fetch Log Categories**
   ```http
   GET /api/sonicos/reporting/log/categories
   Response: {
     "categories": ["System", "Attack", "Network", ...]
   }
   ```

2. **Fetch Logs**
   ```http
   GET /api/sonicos/reporting/log/view
   Parameters:
     startTime: YYYY-MM-DD-HH-MM-SS
     endTime: YYYY-MM-DD-HH-MM-SS
     pageSize: number
     pageIndex: number
     sortBy: "timestamp"
     sortOrder: "desc"
     type: "INFORMATION,NOTICE,ALERT"
   Response: [
     {
       "time": "UTC MM/DD/YYYY HH:MM:SS",
       "id": number,
       "category": "System",
       "priority": "Notice",
       "src_int_": string | null,
       "dst_int_": string | null,
       "src_ip": string,
       "src_port": number,
       "dst_ip": string,
       "dst_port": number,
       "ip_protocol": string | null,
       "user_name": string | null,
       "application": string | null,
       "notes": string,
       "message": string
     }
   ]
   ```

### Important Notes on Log Handling

1. **Timestamp Formats**
   - SonicWall returns timestamps in UTC format: "UTC MM/DD/YYYY HH:MM:SS"
   - When storing in database, convert to local timezone
   - When displaying in UI, use local timezone
   - Timezone conversion must happen at data collection time

2. **Priority to Severity Mapping**
   ```python
   PRIORITY_TO_SEVERITY = {
       "ALERT": "ALERT",
       "CRITICAL": "ALERT",
       "ERROR": "ALERT",
       "WARNING": "NOTICE",
       "NOTICE": "NOTICE",
       "INFO": "INFORMATION",
       "INFORMATION": "INFORMATION",
       None: "INFORMATION"
   }
   ```

3. **Log Collection Best Practices**
   - Collect logs every 5 minutes
   - Use overlapping time windows to prevent missing logs
   - Handle timezone conversion at collection time
   - Store timestamps with timezone info in database
   - Validate all fields before storing
   - Handle null values appropriately

4. **Known Issues**
   - VPN status endpoint may return 400 error
   - Some fields may be null in log entries
   - Timestamps require careful handling of timezones
   - Sample metrics data needs to be replaced with real data
 