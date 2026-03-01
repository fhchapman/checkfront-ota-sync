# Checkfront + Viator / Get Your Guide Sync Layer

This project implements a **custom sync layer** so that:

1. **Net price** from Viator (and later Get Your Guide) appears in Checkfront (as booking notes; invoices stay zeroed by native integration but you have a single source of truth for supplier payout).
2. **Cancellations** in Viator (and later Get Your Guide) update the corresponding booking status in Checkfront (e.g. to VOID).
3. **Amendments** (e.g. time/date changes) are recorded in Checkfront as notes so staff can update manually if needed.

The native Checkfront Viator/GYG integrations do not support cancellation sync or net pricing on invoices; this app fills that gap using your API keys.

**You can run with Viator only.** Get Your Guide API credentials can be added later when available; the app does not require them for Viator cancellation/amendment sync or Viator net-price sync.

---

## Requirements

- Python 3.8+
- **Checkfront** API key and secret (from Checkfront Developer API)
- **Viator** API key and supplier ID (from Viator connectivity details) — required for Viator sync
- **Get Your Guide** (optional for now): add API key when you have it; GYG sync can be enabled later

---

## Setup (Viator-only)

To run with **Viator only** (no Get Your Guide yet), you only need Checkfront + Viator credentials in `.env`. Leave Get Your Guide placeholders as-is until you have API access.

1. **Clone or copy this folder** to your machine or server.

2. **Install dependencies:**

   ```bash
   cd checkfront-ota-sync
   pip install -r requirements.txt
   ```

3. **Configure environment:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set at least:

   - `CHECKFRONT_HOST` – your Checkfront host (e.g. `your-company.checkfront.com`)
   - `CHECKFRONT_API_KEY` – API key from Checkfront
   - `CHECKFRONT_API_SECRET` – API secret from Checkfront

   Optional:

   - `CHECKFRONT_CANCELLED_STATUS` – status to set when OTA cancels (default: `VOID`)
   - `VIATOR_API_KEY` and `VIATOR_SUPPLIER_ID` – from Viator connectivity details (needed for Viator sync)
   - `GETYOURGUIDE_API_KEY` – optional; leave as placeholder until you have GYG API access

4. **Validate:**

   ```bash
   python validate.py
   ```

   This checks that Checkfront credentials work.

---

## 1. Cancellation and amendment sync (Viator → Checkfront) — Viator only for now

Viator calls *your* reservation system when a booking is cancelled or amended. Today that is Checkfront, but Checkfront’s native integration does not apply those updates. So you have two options:

### Option A: Run this app as the “reservation system” for Viator (recommended)

Run the webhook server and expose it over HTTPS (use a tunnel or host on a server with a domain). Then in Viator’s integration configuration, set the reservation system base URL to this app instead of Checkfront, and have this app:

- Receive Viator’s **booking**, **booking-cancellation**, and **booking-amendment** calls.
- For **booking**: either forward to Checkfront API to create the booking, or leave booking creation to Checkfront’s native integration and only use this app for cancel/amend (if Viator allows different URLs per operation).
- For **booking-cancellation** and **booking-amendment**: this app updates Checkfront via API (status + notes) and returns success to Viator.

**Run the webhook server:**

```bash
python run_webhook_server.py
```

By default it listens on port 5000. Set `PORT` in `.env` if needed.

**Viator endpoints this app exposes:**

- `POST /viator/booking-cancellation` – Viator sends cancellation here; we set the Checkfront booking to cancelled (e.g. VOID) and add a note.
- `POST /viator/booking-amendment` – Viator sends amendments here; we add a note to the Checkfront booking.

You must configure Viator to call these URLs (e.g. `https://your-server.com/viator/booking-cancellation`). If Viator is currently pointed at Checkfront, you will need to change that to this app’s URL (and optionally have this app forward new bookings to Checkfront if you fully replace the native integration).

### Option B: Keep Viator → Checkfront for booking creation

If Viator keeps sending new bookings directly to Checkfront, you can still run this app and ask Viator (or Checkfront support) whether cancellation/amendment can be sent to a separate URL (this app). If yes, point those to the same endpoints above.

---

## 2. Net price sync (Viator / Get Your Guide → Checkfront)

Checkfront does not show Viator/GYG net amount on the invoice. This app adds the **net amount (supplier payout)** as a **booking note** in Checkfront so you have an audit trail and can reconcile with Viator/GYG payout reports.

**From a CSV file (e.g. export from Viator/GYG payout reports):**

1. Create a CSV with columns:
   - `checkfront_code` – Checkfront booking code (e.g. CFPP-290317)
   - `net_amount` – amount you are paid (supplier payout)
   - `currency` (optional, default USD)
   - `source` (optional, e.g. Viator, Get Your Guide)

2. Run:

   ```bash
   python run_net_price_sync.py path/to/your_file.csv
   ```

Example CSV:

```csv
checkfront_code,net_amount,currency,source
CFPP-290317,428.28,USD,Viator
CFPP-290318,150.00,EUR,Get Your Guide
```

A sample file is in `config/sample_net_amounts.csv`.

---

## 3. Get Your Guide (optional — add later)

Get Your Guide API credentials are not required to run the sync. When you have GYG API access, add `GETYOURGUIDE_API_KEY` (and optional `GETYOURGUIDE_SUPPLIER_ID`) to `.env`. The app exposes `POST /gyg/cancellation` for GYG callbacks; you can configure that once GYG is set up. If GYG sends a booking id that is not the Checkfront code, add a mapping from GYG booking id → Checkfront code in `webhook_server.py` / `gyg_adapter.py`.

---

## Project layout

- `src/checkfront_client.py` – Checkfront API 3.0 client (list bookings, update status, add note).
- `src/viator_adapter.py` – Parse Viator cancellation/amendment payloads.
- `src/gyg_adapter.py` – Parse Get Your Guide cancellation/update payloads.
- `src/sync.py` – Apply cancellation/amendment and net amount to Checkfront.
- `src/webhook_server.py` – Flask server for Viator/GYG callbacks.
- `src/net_price_sync.py` – Net price sync from CSV.
- `src/config.py` – Load config from `.env`.
- `validate.py` – Check config and Checkfront connectivity.
- `run_webhook_server.py` – Start the webhook server.
- `run_net_price_sync.py` – Run net price sync from CSV.

---

## Validation and testing

1. **Config and Checkfront:**  
   `python validate.py`

2. **Spot-check invoices:**  
   After running net price sync, open a few bookings in Checkfront and confirm the note shows the correct net amount.

3. **Test cancellation sync:**  
   With the webhook server running and Viator pointed at it, cancel a test booking in Viator and confirm the corresponding Checkfront booking’s status changes to VOID (or your `CHECKFRONT_CANCELLED_STATUS`).

---

## API keys and docs

- **Checkfront:** Manage > Integrations > API. See [Checkfront API 3.0](https://api.checkfront.com/ref/).
- **Viator:** [Viator Supplier API](https://docs.viator.com/supplier-api/technical/) (booking, booking-cancellation, booking-amendment).
- **Get Your Guide:** Supplier/partner portal and API docs (exact URLs depend on your GYG setup).

Store API keys only in `.env`; do not commit `.env` to version control.
