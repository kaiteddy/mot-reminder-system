"""
DVLA MOT History API Integration Service

This service handles communication with the real DVLA MOT History Trade API.
No mock data - all responses are from the live DVLA service.
"""

import requests
import os
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class DVLAApiService:
    def __init__(self):
        # DVLA MOT History Trade API credentials - MUST be set via environment variables
        self.client_id = os.environ.get('DVLA_CLIENT_ID')
        self.client_secret = os.environ.get('DVLA_CLIENT_SECRET')
        self.api_key = os.environ.get('DVLA_API_KEY')
        self.tenant_id = os.environ.get('DVLA_TENANT_ID')

        # Validate that all required credentials are present
        if not all([self.client_id, self.client_secret, self.api_key, self.tenant_id]):
            raise ValueError(
                "Missing required DVLA API credentials. Please set environment variables: "
                "DVLA_CLIENT_ID, DVLA_CLIENT_SECRET, DVLA_API_KEY, DVLA_TENANT_ID"
            )

        # API endpoints
        self.token_url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'
        self.api_base_url = 'https://history.mot.api.gov.uk/v1/trade/vehicles'
        self.scope = 'https://tapi.dvsa.gov.uk/.default'

        # Token management
        self.access_token = None
        self.token_expiry = None

    def _get_access_token(self):
        """
        Get an OAuth access token from Microsoft Azure AD for DVLA API access.
        Tokens are valid for one hour.
        """
        try:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': self.scope
            }

            logger.info(f"Requesting OAuth token from: {self.token_url}")

            response = requests.post(self.token_url, headers=headers, data=data, timeout=30)

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                # Tokens expire in 1 hour, set expiry slightly earlier for safety
                expires_in = token_data.get('expires_in', 3600)
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
                logger.info(f"OAuth token obtained successfully, expires at: {self.token_expiry}")
                return self.access_token
            else:
                logger.error(f"Failed to get OAuth token: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting OAuth token: {e}")
            return None

    def _ensure_valid_token(self):
        """Ensure we have a valid access token"""
        if not self.access_token or not self.token_expiry or datetime.now() >= self.token_expiry:
            logger.info("Token expired or missing, requesting new token...")
            return self._get_access_token()
        return self.access_token

    def _clean_registration(self, registration):
        """Clean registration number for API call"""
        if not registration:
            return None
        # Remove spaces and convert to uppercase
        return registration.replace(' ', '').upper()

    def get_vehicle_details(self, registration):
        """
        Get vehicle details from the DVLA MOT History Trade API.
        Returns real data from the official DVLA service.
        """
        # Clean the registration number
        clean_reg = self._clean_registration(registration)
        if not clean_reg:
            logger.warning("Invalid registration number provided")
            return None

        # Ensure we have a valid access token
        token = self._ensure_valid_token()
        if not token:
            logger.error("Failed to obtain access token for DVLA API")
            return None

        try:
            # Make actual DVLA MOT History API call
            headers = {
                'Authorization': f'Bearer {token}',
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            }

            # The DVLA MOT History API endpoint for single vehicle lookup
            url = f'{self.api_base_url}/registration/{clean_reg}'

            logger.info(f"Making DVLA MOT History API call to: {url}")

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"DVLA API success for {clean_reg}")
                return self._process_dvla_response(data)
            elif response.status_code == 404:
                logger.warning(f"Vehicle not found in DVLA records: {clean_reg}")
                return None
            elif response.status_code == 401:
                logger.warning(f"DVLA API authentication failed - token may be invalid")
                # Try to refresh token and retry once
                self.access_token = None
                token = self._ensure_valid_token()
                if token:
                    headers['Authorization'] = f'Bearer {token}'
                    response = requests.get(url, headers=headers, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"DVLA API success for {clean_reg} after token refresh")
                        return self._process_dvla_response(data)
                return None
            else:
                logger.error(f"DVLA API error {response.status_code}: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"DVLA API request failed for {clean_reg}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling DVLA API for {clean_reg}: {e}")
            return None

    def _process_dvla_response(self, data):
        """
        Process the DVLA MOT History API response and extract vehicle information.
        The API returns comprehensive vehicle and MOT history data.
        """
        try:
            # The DVLA MOT History API returns an array of vehicles
            # Usually just one vehicle for a registration lookup
            if not data or len(data) == 0:
                logger.warning("No vehicle data returned from DVLA API")
                return None

            # Get the first (and usually only) vehicle record
            vehicle_data = data[0] if isinstance(data, list) else data

            # Extract basic vehicle information
            processed_data = {
                "registrationNumber": vehicle_data.get('registration'),
                "make": vehicle_data.get('make'),
                "model": vehicle_data.get('model'),
                "primaryColour": vehicle_data.get('primaryColour'),
                "yearOfManufacture": vehicle_data.get('manufactureYear'),
                "engineCapacity": vehicle_data.get('engineSize'),
                "fuelType": vehicle_data.get('fuelType'),
                "co2Emissions": vehicle_data.get('co2Emissions'),
            }

            # Extract MOT information from the most recent MOT test
            mot_tests = vehicle_data.get('motTests', [])
            if mot_tests:
                # MOT tests are usually ordered by date, get the most recent
                latest_mot = mot_tests[0]
                processed_data.update({
                    "motStatus": latest_mot.get('testResult', 'Unknown'),
                    "motExpiryDate": latest_mot.get('expiryDate'),
                    "motTestDate": latest_mot.get('completedDate'),
                    "motTestNumber": latest_mot.get('motTestNumber'),
                    "motTestMileage": latest_mot.get('odometerValue'),
                })

                # Extract defects/advisories if any
                defects = latest_mot.get('rfrAndComments', [])
                if defects:
                    processed_data["motDefects"] = defects
            else:
                processed_data.update({
                    "motStatus": "No MOT History",
                    "motExpiryDate": None,
                    "motTestDate": None,
                    "motTestNumber": None,
                    "motTestMileage": None,
                })

            # Add additional vehicle details if available
            if 'dvlaId' in vehicle_data:
                processed_data["dvlaId"] = vehicle_data['dvlaId']
            if 'firstUsedDate' in vehicle_data:
                processed_data["firstUsedDate"] = vehicle_data['firstUsedDate']

            logger.info(f"Processed DVLA data for {processed_data.get('registrationNumber')}")
            return processed_data

        except Exception as e:
            logger.error(f"Error processing DVLA response: {e}")
            return None
