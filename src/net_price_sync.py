"""
Net price sync: write supplier payout (net) from Viator/Get Your Guide into Checkfront.
Checkfront native integration does not put net amount on the invoice; we add it as a booking note
so you have a single place to see what you are paid. Optionally use for reporting or manual invoice adjustment.
"""
import csv
import logging
import sys

from .config import get_checkfront_config
from .checkfront_client import CheckfrontClient
from .sync import apply_net_amount_note

logger = logging.getLogger(__name__)


def sync_net_amount_from_csv(
    csv_path: str,
    checkfront_code_column: str = "checkfront_code",
    net_amount_column: str = "net_amount",
    currency_column: str = "currency",
    source_column: str = "source",
    default_currency: str = "USD",
    default_source: str = "OTA",
) -> int:
    """
    Read a CSV with columns: checkfront_code, net_amount, currency (optional), source (optional).
    For each row, add a note to the Checkfront booking with the net amount.
    Returns number of rows processed successfully.
    """
    cfg = get_checkfront_config()
    if not cfg["host"] or not cfg["api_key"] or not cfg["api_secret"]:
        raise ValueError("Set CHECKFRONT_HOST, CHECKFRONT_API_KEY, CHECKFRONT_API_SECRET")
    client = CheckfrontClient(
        host=cfg["host"],
        api_key=cfg["api_key"],
        api_secret=cfg["api_secret"],
        cancelled_status=cfg.get("cancelled_status", "VOID"),
    )
    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = (row.get(checkfront_code_column) or "").strip()
            if not code:
                continue
            try:
                net = float(row.get(net_amount_column) or 0)
            except (TypeError, ValueError):
                logger.warning("Skipping row: invalid net_amount for %s", code)
                continue
            currency = (row.get(currency_column) or default_currency).strip()
            source = (row.get(source_column) or default_source).strip()
            if apply_net_amount_note(client, code, net, currency, source):
                count += 1
    return count


def add_net_amount_for_booking(
    checkfront_booking_code: str,
    net_amount: float,
    currency: str = "USD",
    source: str = "Viator",
) -> bool:
    """
    One-off: add net amount note to a single Checkfront booking.
    Use when you have the value from Viator/GYG payout report or API.
    """
    cfg = get_checkfront_config()
    if not cfg["host"] or not cfg["api_key"] or not cfg["api_secret"]:
        raise ValueError("Set CHECKFRONT_HOST, CHECKFRONT_API_KEY, CHECKFRONT_API_SECRET")
    client = CheckfrontClient(
        host=cfg["host"],
        api_key=cfg["api_key"],
        api_secret=cfg["api_secret"],
        cancelled_status=cfg.get("cancelled_status", "VOID"),
    )
    return apply_net_amount_note(client, checkfront_booking_code, net_amount, currency, source)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) < 2:
        print("Usage: python -m src.net_price_sync <csv_path>")
        print("CSV columns: checkfront_code, net_amount, currency (optional), source (optional)")
        sys.exit(1)
    n = sync_net_amount_from_csv(sys.argv[1])
    print(f"Processed {n} rows.")
