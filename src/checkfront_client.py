"""
Checkfront API 3.0 client for listing bookings, updating status, and adding notes (e.g. net amount).
Uses Token authentication: API Key = HTTP Basic username, API Secret = HTTP Basic password.
See: https://api.checkfront.com/ref/ and https://api.checkfront.com/overview/auth.html
"""
import base64
import requests
from typing import Any, Optional


class CheckfrontClient:
    def __init__(
        self,
        host: str,
        api_key: str,
        api_secret: str,
        cancelled_status: str = "VOID",
    ):
        self.host = host.rstrip("/").replace("https://", "").replace("http://", "")
        self.api_key = api_key
        self.api_secret = api_secret
        self.cancelled_status = cancelled_status
        self.base = f"https://{self.host}/api/3.0"
        credentials = f"{api_key}:{api_secret}"
        self.auth_header = "Basic " + base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> dict:
        path_clean = path if path.startswith("/") else f"/{path}"
        full_path = f"/api/3.0{path_clean}" if not path_clean.startswith("/api/3.0") else path_clean
        url = f"https://{self.host}{full_path}"
        headers = {
            "Authorization": self.auth_header,
            "Accept": "application/json",
            "X-Forwarded-For": "127.0.0.1",
        }
        if method == "POST" and params:
            # Checkfront expects url-encoded body for POST with params
            r = requests.request(
                method, url, data=params, headers=headers, timeout=30
            )
        else:
            r = requests.request(
                method, url, params=params, json=json, headers=headers, timeout=30
            )
        r.raise_for_status()
        return r.json()

    def list_bookings(
        self,
        status_id: Optional[str] = None,
        last_modified: Optional[str] = None,
        partner_id: Optional[str] = None,
        limit: int = 100,
        page: int = 1,
    ) -> dict:
        """GET /api/3.0/booking/index. Use last_modified for incremental sync."""
        params = {"limit": limit, "page": page}
        if status_id:
            params["status_id"] = status_id
        if last_modified:
            params["last_modified"] = f">{last_modified}"
        if partner_id:
            params["partner_id"] = partner_id
        return self._request("GET", "/booking/index", params=params)

    def get_booking(self, booking_id: str) -> dict:
        """GET /api/3.0/booking/{booking_id}."""
        return self._request("GET", f"/booking/{booking_id}")

    def update_booking_status(
        self,
        booking_id: str,
        status_id: str,
        notify: bool = False,
    ) -> dict:
        """POST /api/3.0/booking/{booking_id}/update. status_id e.g. VOID, PAID, PEND."""
        return self._request(
            "POST",
            f"/booking/{booking_id}/update",
            params={"status_id": status_id, "notify": "1" if notify else "0"},
        )

    def add_booking_note(self, booking_id: str, body: str) -> dict:
        """POST /api/3.0/booking/{booking_id}/note. Use for net amount or OTA reference."""
        return self._request(
            "POST",
            f"/booking/{booking_id}/note",
            params={"body": body[:3000]},
        )

    def set_booking_cancelled(self, booking_id: str, notify: bool = False) -> dict:
        """Set booking to cancelled status (default VOID)."""
        return self.update_booking_status(
            booking_id, self.cancelled_status, notify=notify
        )

    def find_booking_by_code(self, code: str) -> Optional[dict]:
        """Find a booking by its code (e.g. CFPP-290317 or Viator SupplierConfirmationNumber).
        Checkfront booking/index does not filter by code; we list and search.
        For large accounts, use last_modified or partner_id to narrow.
        """
        page = 1
        while True:
            data = self.list_bookings(limit=100, page=page)
            bookings = data.get("booking/index") or data.get("booking") or {}
            if not bookings:
                break
            for bid, b in (bookings.items() if isinstance(bookings, dict) else []):
                if isinstance(b, dict) and b.get("code") == code:
                    return b
            total = data.get("request", {}).get("total_records", 0)
            if page * 100 >= total:
                break
            page += 1
        return None
