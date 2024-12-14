import uuid
import hashlib
import requests
from typing import Dict, Optional
from urllib.parse import urlparse
from app.core.config import settings
import urllib3
import os

# Disable SSL warnings when verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SonicWallClient:
    def __init__(self):
        self.base_url = f"https://{settings.SONICWALL_HOST}:{settings.SONICWALL_PORT}"
        self.session = requests.Session()
        self.session.verify = settings.SONICWALL_VERIFY_SSL
        self._auth_headers = {}

    def _generate_cnonce(self) -> str:
        """Generate a client nonce."""
        return hashlib.sha256(os.urandom(8)).hexdigest()[:16]

    def _parse_auth_header(self, auth_header: str) -> Dict[str, str]:
        """Parse the WWW-Authenticate header."""
        # Remove 'Digest ' prefix and split into key-value pairs
        parts = auth_header[7:].split(',')
        auth_params = {}
        
        for part in parts:
            key, value = [p.strip() for p in part.split('=', 1)]
            # Remove quotes if present
            auth_params[key] = value.strip('"')
            
        return auth_params

    def _calculate_response(self, auth_params: Dict[str, str], username: str, password: str, method: str, uri: str) -> str:
        """Calculate the digest authentication response."""
        realm = auth_params['realm']
        nonce = auth_params['nonce']
        qop = auth_params.get('qop', 'auth')
        opaque = auth_params.get('opaque', '')
        algorithm = auth_params.get('algorithm', 'SHA-256')
        cnonce = self._generate_cnonce()
        nc = "00000001"

        # Calculate HA1 = SHA-256(username:realm:password)
        ha1 = hashlib.sha256(f"{username}:{realm}:{password}".encode()).hexdigest()
        
        # Calculate HA2 = SHA-256(method:uri)
        ha2 = hashlib.sha256(f"{method}:{uri}".encode()).hexdigest()
        
        # Calculate response = SHA-256(HA1:nonce:nc:cnonce:qop:HA2)
        response = hashlib.sha256(
            f"{ha1}:{nonce}:{nc}:{cnonce}:{qop}:{ha2}".encode()
        ).hexdigest()

        # Build authorization header
        auth_string = (
            f'Digest username="{username}", '
            f'realm="{realm}", '
            f'nonce="{nonce}", '
            f'uri="{uri}", '
            f'algorithm="{algorithm}", '
            f'qop="{qop}", '
            f'nc={nc}, '
            f'cnonce="{cnonce}", '
            f'response="{response}"'
        )

        # Add opaque if present
        if opaque:
            auth_string += f', opaque="{opaque}"'

        return auth_string

    async def authenticate(self) -> bool:
        """
        Perform digest authentication with the SonicWall device.
        Returns True if authentication is successful.
        """
        auth_endpoint = "/api/sonicos/auth"
        
        try:
            print(f"Step 1: Getting authentication challenge from {self.base_url}{auth_endpoint}")
            # Step 1: Get the authentication challenge
            response = self.session.get(
                f"{self.base_url}{auth_endpoint}",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            )

            if response.status_code != 401:
                print(f"Unexpected status code: {response.status_code}")
                print(f"Response headers: {response.headers}")
                print(f"Response body: {response.text}")
                raise Exception(f"Expected 401 response with auth challenge, got {response.status_code}")

            # Get WWW-Authenticate header
            auth_header = response.headers.get('WWW-Authenticate')
            if not auth_header:
                raise Exception("No WWW-Authenticate header in response")

            print("Got WWW-Authenticate header:", auth_header)

            # Parse authentication parameters
            auth_params = self._parse_auth_header(auth_header)
            print("Parsed auth parameters:", auth_params)

            # Calculate digest response
            auth_string = self._calculate_response(
                auth_params,
                settings.SONICWALL_USERNAME,
                settings.SONICWALL_PASSWORD,
                "POST",
                auth_endpoint
            )

            print("Step 2: Sending authentication response")
            # Step 2: Send authentication response
            headers = {
                "Authorization": auth_string,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Connection": "keep-alive",
                "X-SONICOS-API-VERSION": settings.SONICWALL_API_VERSION
            }

            auth_response = self.session.post(
                f"{self.base_url}{auth_endpoint}",
                headers=headers,
                json={}  # Empty JSON body
            )

            print(f"Auth response status: {auth_response.status_code}")
            print(f"Auth response headers: {auth_response.headers}")
            print(f"Auth response body: {auth_response.text}")

            if auth_response.status_code != 200:
                raise Exception(f"Authentication failed: {auth_response.status_code}")

            # Store authentication headers for future requests
            self._auth_headers = headers

            print("Step 3: Starting management session")
            # Step 3: Start management session
            management_response = self.session.post(
                f"{self.base_url}/api/sonicos/start-management",
                headers=self._auth_headers,
                data=None  # No body at all
            )

            print(f"Management response status: {management_response.status_code}")
            print(f"Management response headers: {management_response.headers}")
            print(f"Management response body: {management_response.text}")

            if management_response.status_code != 200:
                raise Exception("Failed to start management session")

            return True

        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False

    async def get_security_services_status(self) -> Optional[Dict]:
        """
        Get the status of security services.
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/sonicos/reporting/status/security-services",
                headers=self._auth_headers
            )
            response.raise_for_status()
            
            print(f"Security Services Response: {response.text}")  # Debug logging
            
            # For this endpoint, the response is directly the data we want
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting security services status: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error getting security services status: {str(e)}")
            return None

    async def get_gateway_av_status(self) -> Optional[Dict]:
        """
        Get Gateway Anti-Virus status.
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/sonicos/reporting/gateway-antivirus",
                headers=self._auth_headers
            )
            response.raise_for_status()
            
            print(f"Gateway AV Response: {response.text}")  # Debug logging
            
            # Return the response directly as it contains the data we want
            return response.json()
            
        except Exception as e:
            print(f"Error getting Gateway AV status: {str(e)}")
            return None

    async def get_intrusion_prevention_status(self) -> Optional[Dict]:
        """
        Get Intrusion Prevention status.
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/sonicos/reporting/intrusion-prevention",
                headers=self._auth_headers
            )
            response.raise_for_status()
            
            print(f"IPS Response: {response.text}")  # Debug logging
            
            # Return the response directly as it contains the data we want
            return response.json()
            
        except Exception as e:
            print(f"Error getting Intrusion Prevention status: {str(e)}")
            return None

    async def get_botnet_status(self) -> Optional[Dict]:
        """
        Get Botnet Filter status.
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/sonicos/reporting/botnet/status",
                headers=self._auth_headers
            )
            response.raise_for_status()
            
            print(f"Botnet Response: {response.text}")  # Debug logging
            
            # Return the response directly as it contains the data we want
            return response.json()
            
        except Exception as e:
            print(f"Error getting Botnet status: {str(e)}")
            return None

    async def close_session(self) -> bool:
        """Close the management session."""
        try:
            response = self.session.delete(
                f"{self.base_url}/api/sonicos/auth",
                headers=self._auth_headers
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error closing session: {str(e)}")
            return False

    async def get_anti_spyware_status(self) -> Optional[Dict]:
        """
        Get Anti-Spyware status.
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/sonicos/reporting/anti-spyware",
                headers=self._auth_headers
            )
            response.raise_for_status()
            
            print(f"Anti-Spyware Response: {response.text}")  # Debug logging
            
            # Return the response directly as it contains the data we want
            return response.json()
            
        except Exception as e:
            print(f"Error getting Anti-Spyware status: {str(e)}")
            return None

    async def get_content_filtering_status(self) -> Optional[Dict]:
        """
        Get Content Filtering status.
        """
        # List of possible endpoints to try
        endpoints = [
            "/api/sonicos/content-filtering/status",
            "/api/sonicos/reporting/content-filtering",
            "/api/sonicos/cfs/status",
            "/api/sonicos/security-services/content-filtering"
        ]

        for endpoint in endpoints:
            try:
                print(f"Trying endpoint: {endpoint}")
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    headers=self._auth_headers
                )
                response.raise_for_status()
                
                print(f"Content Filtering Response: {response.text}")  # Debug logging
                
                # Return the response directly as it contains the data we want
                return response.json()
                
            except requests.exceptions.RequestException as e:
                print(f"Error with endpoint {endpoint}: {str(e)}")
                continue
            except Exception as e:
                print(f"Unexpected error with endpoint {endpoint}: {str(e)}")
                continue
        
        print("All content filtering endpoints failed")
        return None 