"""
Get Your Guide integration: parse cancellation/amendment and net payout.
GYG API docs: https://supply.getyourguide.support/ (supplier portal).
This adapter normalizes GYG payloads for sync; exact webhook/API shape may vary by GYG setup.
"""
import logging
from typing import Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GYGCancellationEvent:
    """Normalized GYG cancellation event."""
    booking_id: str
    external_reference: Optional[str] = None
    net_amount: Optional[float] = None
    raw: Optional[dict] = None


@dataclass
class GYGBookingUpdate:
    """Normalized GYG booking with status and net payout."""
    booking_id: str
    status: str  # e.g. CONFIRMED, CANCELLED, AMENDED
    net_amount: Optional[float] = None
    currency: Optional[str] = None
    raw: Optional[dict] = None


def parse_gyg_cancellation(body: dict) -> Optional[GYGCancellationEvent]:
    """
    Parse Get Your Guide cancellation payload.
    Adjust keys to match GYG's actual webhook/API response when you have docs.
    """
    try:
        # Common patterns: bookingId, booking_id, externalReference
        bid = (
            body.get("bookingId")
            or body.get("booking_id")
            or body.get("data", {}).get("bookingId")
            or ""
        )
        if not bid:
            return None
        data = body.get("data") or body
        return GYGCancellationEvent(
            booking_id=str(bid),
            external_reference=data.get("externalReference") or data.get("external_reference"),
            net_amount=_safe_float(data.get("netAmount") or data.get("net_amount") or data.get("payout")),
            raw=body,
        )
    except Exception as e:
        logger.warning("Failed to parse GYG cancellation: %s", e)
        return None


def _safe_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_gyg_booking_update(body: dict) -> Optional[GYGBookingUpdate]:
    """Parse GYG booking update (status change / amendment)."""
    try:
        bid = (
            body.get("bookingId")
            or body.get("booking_id")
            or body.get("data", {}).get("bookingId")
            or ""
        )
        if not bid:
            return None
        data = body.get("data") or body
        status = (
            (data.get("status") or data.get("bookingStatus") or "UNKNOWN")
        ).upper()
        return GYGBookingUpdate(
            booking_id=str(bid),
            status=status,
            net_amount=_safe_float(data.get("netAmount") or data.get("net_amount") or data.get("payout")),
            currency=data.get("currency"),
            raw=body,
        )
    except Exception as e:
        logger.warning("Failed to parse GYG booking update: %s", e)
        return None
