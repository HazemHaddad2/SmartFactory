"""Client HTTP pour communiquer avec les microservices"""

import httpx
import logging
from typing import Any, Dict, Optional
from config import REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

class ServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
    
    async def get(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Effectuer une requête GET"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"GET {url} failed: {e}")
            raise
    
    async def post(self, endpoint: str, json: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Effectuer une requête POST"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.post(url, json=json, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"POST {url} failed: {e}")
            raise
    
    async def patch(self, endpoint: str, json: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Effectuer une requête PATCH"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.patch(url, json=json, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"PATCH {url} failed: {e}")
            raise
    
    async def delete(self, endpoint: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Effectuer une requête DELETE"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.delete(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"DELETE {url} failed: {e}")
            raise
    
    async def close(self):
        """Fermer le client"""
        await self.client.aclose()
