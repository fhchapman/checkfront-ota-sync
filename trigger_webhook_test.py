#!/usr/bin/env python3
"""
Manually trigger the Viator webhook for testing.
Usage:
  python3 trigger_webhook_test.py [checkfront_booking_code]
  python3 trigger_webhook_test.py                    # use default base URL and a placeholder code
  python3 trigger_webhook_test.py CFPP-123456        # test with a real Checkfront booking code

Set WEBHOOK_BASE_URL to test against ngrok, e.g.:
  WEBHOOK_BASE_URL=https://expiable-kizzy-overplausible.ngrok-free.dev python3 trigger_webhook_test.py CFPP-123456
"""
import os
import sys
import json
import urllib.request

# Default: local server. Override with env WEBHOOK_BASE_URL for ngrok.
BASE = os.environ.get("WEBHOOK_BASE_URL", "http://localhost:5000")
CHECKFRONT_CODE = (sys.argv[1] if len(sys.argv) > 1 else "TEST-BOOKING-CODE").strip()


def post_cancellation():
    """POST a Viator-style BookingCancellationRequest to the webhook."""
    url = f"{BASE.rstrip('/')}/viator/booking-cancellation"
    payload = {
        "requestType": "BookingCancellationRequest",
        "data": {
            "ApiKey": "test",
            "ResellerId": "1000",
            "SupplierId": "5034073",
            "ExternalReference": "TEST-EXT-12345",
            "Timestamp": "2026-03-01T12:00:00Z",
            "BookingReference": "VIATOR-REF-999",
            "SupplierConfirmationNumber": CHECKFRONT_CODE,
            "CancelDate": "2026-03-01",
            "Author": "Manual test",
            "Reason": "Manual webhook test",
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode()
            print("Status:", resp.status)
            print("Response:", body)
            return resp.status == 200
    except urllib.error.HTTPError as e:
        print("Status:", e.code)
        print("Response:", e.read().decode())
        return False
    except Exception as e:
        print("Error:", e)
        return False


def post_amendment():
    """POST a Viator-style BookingAmendmentRequest to the webhook."""
    url = f"{BASE.rstrip('/')}/viator/booking-amendment"
    payload = {
        "requestType": "BookingAmendmentRequest",
        "data": {
            "ExternalReference": "TEST-EXT-12345",
            "BookingReference": "VIATOR-REF-999",
            "SupplierConfirmationNumber": CHECKFRONT_CODE,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode()
            print("Status:", resp.status)
            print("Response:", body)
            return resp.status == 200
    except urllib.error.HTTPError as e:
        print("Status:", e.code)
        print("Response:", e.read().decode())
        return False
    except Exception as e:
        print("Error:", e)
        return False


if __name__ == "__main__":
    print("Base URL:", BASE)
    print("Checkfront booking code (SupplierConfirmationNumber):", CHECKFRONT_CODE)
    print("\n--- Cancellation webhook ---")
    ok_cancel = post_cancellation()
    print("\n--- Amendment webhook ---")
    ok_amend = post_amendment()
    sys.exit(0 if (ok_cancel and ok_amend) else 1)
