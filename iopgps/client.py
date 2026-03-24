"""
Small reusable HTTP client for standalone IOPGPS testing scripts.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from main import get_access_token

BASE_URL = "https://open.iopgps.com"


class IOPGPSStandaloneClient:
    def __init__(self, appid: str, password: str, base_url: str = BASE_URL):
        self.appid = appid
        self.password = password
        self.base_url = base_url.rstrip("/")
        self._token: Optional[str] = None

    def token(self, refresh: bool = False) -> str:
        if self._token and not refresh:
            return self._token
        token = get_access_token(self.appid, self.password)
        if not token:
            raise RuntimeError("Failed to get IOPGPS access token.")
        self._token = token
        return token

    def request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        token = self.token()
        url = f"{self.base_url}{path}"
        headers = {"accessToken": token}
        response = requests.request(method=method, url=url, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        return response.json()
