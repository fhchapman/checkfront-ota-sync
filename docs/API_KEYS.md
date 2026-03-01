# Where to get API keys

## Checkfront

1. Log in to your Checkfront account.
2. Go to **Manage > Integrations > API** (or **Settings > API** depending on layout).
3. Create or copy your **API Key** and **API Secret**.
4. Your **host** is your Checkfront subdomain, e.g. `your-company.checkfront.com` (no `https://`).

References:

- [Checkfront API 3.0](https://api.checkfront.com/ref/)
- [Request formatting / auth](https://api.checkfront.com/overview/requests.html)

---

## Viator

1. Use your Viator **supplier/partner** account (not the customer site).
2. Open **Connectivity details** (or equivalent) in the Viator integration / partner portal. You should see:
   - **Reservation system:** Checkfront
   - **API key:** (long token) — put this in `.env` as `VIATOR_API_KEY`
   - **API supplier ID:** (numeric, e.g. 5034073) — put this in `.env` as `VIATOR_SUPPLIER_ID`
   - **API enabled:** Yes
3. Copy the API key and supplier ID into your `.env` file. Do not commit `.env` or share the API key.
4. If you use Checkfront’s native Viator channel, Viator sends bookings to Checkfront; for cancellation/amendment sync, point Viator’s callbacks to this sync app or use Viator’s API as needed.
5. Viator Supplier API docs: [Viator Reservation System API](https://docs.viator.com/supplier-api/technical/).

Contact: supplierAPI@viator.com for API integration questions.

---

## Get Your Guide

1. Log in to the **Get Your Guide Supply Partner** portal.
2. API keys and webhook/callback configuration are typically under integration or API settings in the supplier dashboard.
3. Use their help center for “API” or “integration” to find the exact URLs and payload formats for:
   - Booking status / cancellation webhooks
   - Net payout (supplier payout) in booking or payout reports

References:

- [Get Your Guide Supply Partner Help](https://supply.getyourguide.support/)
- Understanding payouts: search for “Bookings for Payout” or “Understanding Bookings for Payout” in their help.

---

## Security

- Never commit `.env` or any file containing API keys to version control.
- Run the webhook server over HTTPS in production.
- Restrict firewall or load balancer so only Viator/GYG IPs (if they provide them) can call your webhook URLs, if possible.
