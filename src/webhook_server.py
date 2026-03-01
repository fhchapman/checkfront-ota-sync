"""
Flask server that receives Viator (and optionally GYG) callbacks for booking cancellation/amendment.
Point Viator's reservation system URLs to this server so we can update Checkfront when Viator cancels or amends.
"""
import logging
from flask import Flask, request, jsonify

from .config import get_checkfront_config, get_viator_config, get_gyg_config
from .checkfront_client import CheckfrontClient
from .viator_adapter import (
    parse_viator_cancellation,
    parse_viator_amendment,
    viator_cancellation_success_response,
)
from .gyg_adapter import parse_gyg_cancellation
from .sync import (
    apply_viator_cancellation,
    apply_viator_amendment,
    apply_gyg_cancellation,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def _checkfront_client() -> CheckfrontClient:
    cfg = get_checkfront_config()
    if not cfg["host"] or not cfg["api_key"] or not cfg["api_secret"]:
        raise ValueError("Checkfront CHECKFRONT_HOST, CHECKFRONT_API_KEY, CHECKFRONT_API_SECRET must be set")
    return CheckfrontClient(
        host=cfg["host"],
        api_key=cfg["api_key"],
        api_secret=cfg["api_secret"],
        cancelled_status=cfg["cancelled_status"],
    )


@app.route("/viator/booking-cancellation", methods=["POST"])
def viator_booking_cancellation():
    """
    Viator calls this when a booking is cancelled.
    Request body: BookingCancellationRequest (JSON).
    We update Checkfront and return BookingCancellationResponse.
    """
    try:
        body = request.get_json(force=True, silent=True) or {}
        event = parse_viator_cancellation(body)
        if not event:
            return jsonify({"error": "Invalid or missing BookingCancellationRequest"}), 400
        client = _checkfront_client()
        ok = apply_viator_cancellation(client, event)
        if ok:
            return jsonify(viator_cancellation_success_response())
        return jsonify({"error": "Failed to update Checkfront"}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.exception("Viator cancellation handler error: %s", e)
        return jsonify({"error": "Internal error"}), 500


@app.route("/viator/booking-amendment", methods=["POST"])
def viator_booking_amendment():
    """
    Viator calls this when a booking is amended (e.g. date/time).
    We add a note to the Checkfront booking; full amendment sync would require Checkfront API support for updating date/time.
    """
    try:
        body = request.get_json(force=True, silent=True) or {}
        event = parse_viator_amendment(body)
        if not event:
            return jsonify({"error": "Invalid or missing BookingAmendmentRequest"}), 400
        client = _checkfront_client()
        ok = apply_viator_amendment(client, event)
        if ok:
            return jsonify({"responseType": "BookingAmendmentResponse", "data": {"RequestStatus": {"Status": "SUCCESS"}}})
        return jsonify({"error": "Failed to update Checkfront"}), 500
    except Exception as e:
        logger.exception("Viator amendment handler error: %s", e)
        return jsonify({"error": "Internal error"}), 500


@app.route("/gyg/cancellation", methods=["POST"])
def gyg_cancellation():
    """
    Get Your Guide cancellation callback (if GYG supports webhook to this URL).
    You may need to map GYG booking_id to Checkfront code via a lookup table or GYG API.
    """
    try:
        body = request.get_json(force=True, silent=True) or {}
        event = parse_gyg_cancellation(body)
        if not event:
            return jsonify({"error": "Invalid or missing GYG cancellation payload"}), 400
        client = _checkfront_client()
        # Without a mapping, we only have event.booking_id; you can add a store or env mapping
        code_from_gyg_id = None  # TODO: resolve GYG booking_id -> Checkfront code
        ok = apply_gyg_cancellation(client, event, code_from_gyg_id=code_from_gyg_id)
        if ok:
            return jsonify({"status": "ok"})
        return jsonify({"error": "Failed to update Checkfront"}), 500
    except Exception as e:
        logger.exception("GYG cancellation handler error: %s", e)
        return jsonify({"error": "Internal error"}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


def run_server(host="0.0.0.0", port=5000):
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    run_server(port=int(__import__("os").environ.get("PORT", "5000")))
