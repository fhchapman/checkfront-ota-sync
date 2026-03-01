#!/usr/bin/env python3
"""
Validate configuration and Checkfront connectivity.
Run after setting .env. Use for spot-check before going live.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    from dotenv import load_dotenv
    load_dotenv()

    errors = []
    # Required for sync
    if not os.environ.get("CHECKFRONT_HOST"):
        errors.append("CHECKFRONT_HOST is not set")
    if not os.environ.get("CHECKFRONT_API_KEY"):
        errors.append("CHECKFRONT_API_KEY is not set")
    if not os.environ.get("CHECKFRONT_API_SECRET"):
        errors.append("CHECKFRONT_API_SECRET is not set")

    if errors:
        print("Configuration errors:")
        for e in errors:
            print("  -", e)
        print("\nCopy .env.example to .env and fill in your API keys.")
        sys.exit(1)

    print("Checking Checkfront connection...")
    try:
        from src.config import get_checkfront_config
        from src.checkfront_client import CheckfrontClient
        cfg = get_checkfront_config()
        client = CheckfrontClient(
            host=cfg["host"],
            api_key=cfg["api_key"],
            api_secret=cfg["api_secret"],
            cancelled_status=cfg.get("cancelled_status", "VOID"),
        )
        # List one page of bookings to verify auth
        data = client.list_bookings(limit=1, page=1)
        status = data.get("request", {}).get("status", "")
        if status == "OK":
            print("Checkfront connection OK.")
        else:
            print("Checkfront returned:", data)
    except Exception as e:
        print("Checkfront connection failed:", e)
        sys.exit(1)

    print("\nValidation passed. Next steps:")
    print("1. Run webhook server: python run_webhook_server.py")
    print("2. Point Viator booking-cancellation and booking-amendment URLs to this server.")
    print("3. For net price: create a CSV with checkfront_code, net_amount, currency, source and run:")
    print("   python run_net_price_sync.py your_file.csv")


if __name__ == "__main__":
    main()
