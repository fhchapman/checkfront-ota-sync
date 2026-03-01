"""
Sync layer: apply Viator and Get Your Guide cancellation/amendment and net price to Checkfront.
- When we receive a cancellation (from webhook or poll), set Checkfront booking to cancelled status.
- When we have net amount, add it as a booking note (Checkfront may not allow setting invoice total via API).
"""
import logging
from typing import Optional

from .checkfront_client import CheckfrontClient
from .viator_adapter import ViatorCancellationEvent, ViatorAmendmentEvent
from .gyg_adapter import GYGCancellationEvent, GYGBookingUpdate

logger = logging.getLogger(__name__)


def apply_viator_cancellation(
    client: CheckfrontClient,
    event: ViatorCancellationEvent,
    add_note: bool = True,
) -> bool:
    """
    When Viator sends a cancellation, update the corresponding Checkfront booking to cancelled.
    Match by SupplierConfirmationNumber (Checkfront booking code).
    """
    code = event.supplier_confirmation_number.strip()
    if not code:
        logger.warning("Viator cancellation missing SupplierConfirmationNumber")
        return False
    # Checkfront booking code is the same as what we sent to Viator (e.g. CFPP-290317)
    try:
        client.set_booking_cancelled(code, notify=False)
        if add_note:
            note = f"[Viator] Cancelled. ExternalReference={event.external_reference}"
            if event.reason:
                note += f" Reason: {event.reason}"
            client.add_booking_note(code, note)
        logger.info("Checkfront booking %s set to cancelled (Viator)", code)
        return True
    except Exception as e:
        logger.exception("Failed to cancel Checkfront booking %s: %s", code, e)
        return False


def apply_viator_amendment(
    client: CheckfrontClient,
    event: ViatorAmendmentEvent,
    note_body: Optional[str] = None,
) -> bool:
    """
    When Viator sends an amendment (e.g. time/date change), add a note to the Checkfront booking.
    Checkfront API update may not support changing date/time; we add a note for staff.
    """
    code = event.supplier_confirmation_number.strip()
    if not code:
        return False
    try:
        if note_body:
            client.add_booking_note(code, note_body)
        else:
            client.add_booking_note(
                code,
                f"[Viator] Amendment received. ExternalReference={event.external_reference}. Please update booking in Checkfront if needed.",
            )
        logger.info("Checkfront booking %s amendment note added", code)
        return True
    except Exception as e:
        logger.exception("Failed to add amendment note to %s: %s", code, e)
        return False


def apply_gyg_cancellation(
    client: CheckfrontClient,
    event: GYGCancellationEvent,
    code_from_gyg_id: Optional[str] = None,
    add_note: bool = True,
) -> bool:
    """
    When GYG sends a cancellation, update Checkfront booking to cancelled.
    We need to resolve GYG booking_id to Checkfront booking code. If you store
    GYG booking id in a Checkfront note or custom field, pass code_from_gyg_id
    (the Checkfront code). Otherwise we would need a mapping store or GYG API to resolve.
    """
    code = code_from_gyg_id or event.external_reference or event.booking_id
    if not code:
        logger.warning("GYG cancellation: no Checkfront code mapping for GYG id %s", event.booking_id)
        return False
    try:
        client.set_booking_cancelled(code, notify=False)
        if add_note:
            note = f"[Get Your Guide] Cancelled. GYG booking id: {event.booking_id}"
            if event.net_amount is not None:
                note += f" Net amount was: {event.net_amount}"
            client.add_booking_note(code, note)
        logger.info("Checkfront booking %s set to cancelled (GYG)", code)
        return True
    except Exception as e:
        logger.exception("Failed to cancel Checkfront booking %s: %s", code, e)
        return False


def apply_net_amount_note(
    client: CheckfrontClient,
    checkfront_booking_code: str,
    net_amount: float,
    currency: str,
    source: str = "OTA",
) -> bool:
    """
    Add a staff-only note with the net amount we are paid (for invoicing/reporting).
    Checkfront may not allow setting invoice total via API; the note preserves the value.
    """
    try:
        body = f"[{source}] Net amount (supplier payout): {currency} {net_amount:.2f}"
        client.add_booking_note(checkfront_booking_code, body)
        logger.info("Added net amount note to %s: %s %s", checkfront_booking_code, currency, net_amount)
        return True
    except Exception as e:
        logger.exception("Failed to add net amount note: %s", e)
        return False
