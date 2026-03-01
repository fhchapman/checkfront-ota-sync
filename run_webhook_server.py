#!/usr/bin/env python3
"""
Run the webhook server so Viator (and optionally GYG) can send cancellation/amendment to this app.
Then we update Checkfront via API.
Configure Viator to call:
  POST https://your-host/viator/booking-cancellation
  POST https://your-host/viator/booking-amendment
"""
import os
import sys

# Run from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.webhook_server import run_server

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    run_server(host="0.0.0.0", port=port)
