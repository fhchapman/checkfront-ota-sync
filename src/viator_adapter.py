"""
Viator integration: parse cancellation/amendment payloads and normalize for sync.
Viator calls the reservation system (POST /booking-cancellation, POST /booking-amendment).
This adapter parses those payloads so we can update Checkfront.
Viator Supplier API: https://docs.viator.com/supplier-api/technical/
"""
import logging
from typing import Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ViatorCancellationEvent:
    """Parsed from Viator Booking Cancellation API request."""
    external_reference: str   # Viator booking ref (ExternalReference)
    booking_reference: str    # Viator BookingReference
    supplier_confirmation_number: str  # Our confirmation (Checkfront code)
    cancel_date: Optional[str] = None
    reason: Optional[str] = None
    raw: Optional[dict] = None


@dataclass
class ViatorAmendmentEvent:
    """Parsed from Viator Booking Amendment API request."""
    external_reference: str
    booking_reference: str
    supplier_confirmation_number: str
    raw: Optional[dict] = None


def parse_viator_cancellation(body: dict) -> Optional[ViatorCancellationEvent]:
    """
    Parse Viator BookingCancellationRequest.
    Example: {"requestType": "BookingCancellationRequest", "data": {"ExternalReference": "...", "BookingReference": "...", "SupplierConfirmationNumber": "CN123456", ...}}
    """
    try:
        if body.get("requestType") != "BookingCancellationRequest":
            return None
        data = body.get("data") or {}
        return ViatorCancellationEvent(
            external_reference=str(data.get("ExternalReference", "")),
            booking_reference=str(data.get("BookingReference", "")),
            supplier_confirmation_number=str(data.get("SupplierConfirmationNumber", "")),
            cancel_date=data.get("CancelDate"),
            reason=data.get("Reason"),
            raw=body,
        )
    except Exception as e:
        logger.warning("Failed to parse Viator cancellation: %s", e)
        return None


def parse_viator_amendment(body: dict) -> Optional[ViatorAmendmentEvent]:
    """Parse Viator Booking Amendment request."""
    try:
        if body.get("requestType") != "BookingAmendmentRequest":
            return None
        data = body.get("data") or {}
        return ViatorAmendmentEvent(
            external_reference=str(data.get("ExternalReference", "")),
            booking_reference=str(data.get("BookingReference", "")),
            supplier_confirmation_number=str(data.get("SupplierConfirmationNumber", "")),
            raw=body,
        )
    except Exception as e:
        logger.warning("Failed to parse Viator amendment: %s", e)
        return None


def viator_cancellation_success_response(supplier_cancellation_number: str = "") -> dict:
    """Build Viator BookingCancellationResponse for success."""
    return {
        "responseType": "BookingCancellationResponse",
        "data": {
            "RequestStatus": {"Status": "SUCCESS"},
            "SupplierCancellationNumber": supplier_cancellation_number or "SYNC-OK",
        },
    }
