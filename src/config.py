"""Load config from environment."""
import os
from dotenv import load_dotenv

load_dotenv()


def get_checkfront_config():
    return {
        "host": os.environ.get("CHECKFRONT_HOST", "").strip(),
        "api_key": os.environ.get("CHECKFRONT_API_KEY", "").strip(),
        "api_secret": os.environ.get("CHECKFRONT_API_SECRET", "").strip(),
        "cancelled_status": os.environ.get("CHECKFRONT_CANCELLED_STATUS", "VOID").strip(),
    }


def get_viator_config():
    return {
        "api_key": os.environ.get("VIATOR_API_KEY", "").strip(),
        "supplier_id": os.environ.get("VIATOR_SUPPLIER_ID", "").strip(),
        "api_base_url": os.environ.get("VIATOR_API_BASE_URL", "https://api.viator.com").strip(),
        "callback_base_url": os.environ.get("VIATOR_CALLBACK_BASE_URL", "").strip(),
    }


def get_gyg_config():
    return {
        "api_key": os.environ.get("GETYOURGUIDE_API_KEY", "").strip(),
        "api_base_url": os.environ.get("GETYOURGUIDE_API_BASE_URL", "https://api.getyourguide.com").strip(),
    }


def get_sync_config():
    return {
        "poll_interval_seconds": int(os.environ.get("SYNC_POLL_INTERVAL", "300") or "300"),
    }
