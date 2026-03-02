# Run the webhook server on AWS Lambda

This guide sets up your Checkfront–Viator webhook app on **AWS Lambda** behind **API Gateway**, so Viator can call your endpoints 24/7 without running a server. You get **1 million requests/month free** (Lambda always; API Gateway for the first 12 months).

---

## What you need

- An **AWS account**
- Your **Checkfront and Viator** env vars (same as `.env` locally)
- **Python 3.11** (or 3.12) for building the deployment package

---

## 1. Build the deployment package

From your project root (`checkfront-ota-sync`):

```bash
cd /Users/frankchapman/Desktop/checkfront-ota-sync

# Create a clean directory for the package
mkdir -p build/lambda_package
cd build/lambda_package

# Install dependencies (same Python version you'll use on Lambda, e.g. 3.11)
pip install -r ../../requirements.txt -t . --upgrade

# Copy your application code
cp ../../lambda_handler.py .
cp -r ../../src .

# Zip everything (Lambda expects the handler and "src" at the root of the zip)
zip -r ../lambda_deploy.zip .
cd ..
# lambda_deploy.zip is ready to upload
```

You should have `build/lambda_deploy.zip` (often 5–15 MB with Flask and dependencies).

---

## 2. Create the Lambda function

1. In **AWS Console** go to **Lambda** → **Functions** → **Create function**.
2. **Name:** e.g. `checkfront-viator-webhook`.
3. **Runtime:** **Python 3.11** (or 3.12).
4. **Architecture:** x86_64 (default).
5. Leave **Execution role** as “Create a new role with basic Lambda permissions.”
6. **Create function**.

### Upload the zip

- **Code** → **Upload from** → **.zip file** → choose `build/lambda_deploy.zip`.
- **Runtime settings** → **Edit** → set **Handler** to:  
  `lambda_handler.lambda_handler`  
  Save.

### Set environment variables

In the function, go to **Configuration** → **Environment variables** → **Edit** → **Add** each of these (use the same values as in your `.env`):

| Key | Example / description |
|-----|------------------------|
| `CHECKFRONT_HOST` | `heartsix.checkfront.com` |
| `CHECKFRONT_API_KEY` | Your Checkfront API key |
| `CHECKFRONT_API_SECRET` | Your Checkfront API secret |
| `CHECKFRONT_CANCELLED_STATUS` | `VOID` (optional) |
| `VIATOR_API_KEY` | Your Viator API key |
| `VIATOR_SUPPLIER_ID` | e.g. `5034073` |

(Add `GETYOURGUIDE_*` later if you use Get Your Guide.)

Save.

### Optional: increase timeout

- **Configuration** → **General configuration** → **Edit**.
- Set **Timeout** to **30** seconds (Viator and Checkfront can be slow).
- Save.

---

## 3. Create API Gateway (HTTP API)

You need a public URL that forwards requests to Lambda.

1. In **AWS Console** go to **API Gateway** → **Create API**.
2. Choose **HTTP API** → **Build**.
3. **Integrations** → **Add integration** → **Lambda**.
   - Select your function: `checkfront-viator-webhook`.
   - API Gateway will ask to add a **resource-based policy** to the Lambda so API Gateway can invoke it → confirm **OK**.
4. **API name:** e.g. `checkfront-viator-webhook`.
5. **Create**.

### Add routes

In the API, go to **Routes** and add:

| Method | Path | Integration |
|--------|------|-------------|
| `POST` | `/viator/booking-cancellation` | Lambda `checkfront-viator-webhook` |
| `POST` | `/viator/booking-amendment` | Lambda `checkfront-viator-webhook` |
| `GET`  | `/health` | Lambda `checkfront-viator-webhook` |

For each route:

- **Create** route → set **Method** and **Path**.
- **Attach integration** → choose the Lambda integration.

### Get your URL

- **Stages** → select **$default** (or create a stage).
- Copy the **Invoke URL**, e.g.  
  `https://abc123xyz.execute-api.us-east-1.amazonaws.com`

Your Viator endpoints will be:

- **Cancellation:** `https://YOUR-API-ID.execute-api.REGION.amazonaws.com/viator/booking-cancellation`
- **Amendment:** `https://YOUR-API-ID.execute-api.REGION.amazonaws.com/viator/booking-amendment`
- **Health:** `https://YOUR-API-ID.execute-api.REGION.amazonaws.com/health`

---

## 4. Point Viator to Lambda

In **Viator’s integration/connectivity settings**, set:

- **Booking cancellation URL:**  
  `https://YOUR-API-ID.execute-api.REGION.amazonaws.com/viator/booking-cancellation`
- **Booking amendment URL:**  
  `https://YOUR-API-ID.execute-api.REGION.amazonaws.com/viator/booking-amendment`

Use the exact **Invoke URL** from API Gateway and the paths above.

---

## 5. Test

**Health check:**

```bash
curl https://YOUR-API-ID.execute-api.REGION.amazonaws.com/health
# Expected: {"status":"ok"}
```

**Webhook test (same as local, but against Lambda URL):**

```bash
cd /Users/frankchapman/Desktop/checkfront-ota-sync
WEBHOOK_BASE_URL=https://YOUR-API-ID.execute-api.REGION.amazonaws.com python3 trigger_webhook_test.py
```

You should see **Status: 200** and **SUCCESS** for cancellation and amendment.

---

## 6. Redeploy after code changes

1. Rebuild the zip (same as step 1).
2. In Lambda → **Code** → **Upload from** → **.zip file** → upload the new zip.
3. Save. No need to change API Gateway.

---

## Troubleshooting

- **502 / 500 from API Gateway:** Check **CloudWatch** → **Log groups** → `/aws/lambda/checkfront-viator-webhook` for Python errors and Checkfront/Viator API errors.
- **Timeout:** Increase Lambda timeout (e.g. 30 s) and ensure Checkfront/Viator keys and URLs are correct.
- **Missing env vars:** Confirm every variable from your `.env` that the app uses is set in Lambda **Environment variables**.

---

## Cost (at low volume)

- **Lambda:** 1 million requests/month free, then about $0.20 per next million.
- **API Gateway (HTTP API):** 1 million calls/month free for the first 12 months; then about $1.00 per million.

For hundreds or a few thousand calls per month, expect **$0** while within free tier.
