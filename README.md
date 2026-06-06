# Cap CAPTCHA Template

Standalone CAPTCHA service for web forms, providing Proof-of-Work (PoW), Honeypot, and Proxy services for external CAPTCHA providers.

## Features

- **PoW Challenges**: Request a computational challenge to thwart simple bots.
- **Honeypot Verification**: Simple check for hidden fields.
- **Cap Proxy**: CORS-enabled proxy for the Cap CAPTCHA service.
- **Unified Verification API**: One endpoint to verify different types of human proof.

## Setup

### Environment Variables

- `CAP_ENDPOINT`: The URL of the underlying Cap CAPTCHA service.
- `CAP_SECRET_KEY`: The secret key for Cap verification.
- `POW_DEFAULT_DIFFICULTY`: Default difficulty for PoW challenges (default: 4).

## API Usage

### 1. Proof-of-Work (PoW)
- **Request Challenge**: `GET /pow-challenge?difficulty=4`
- **Verify**: `POST /verify` with body `{"pow_secret": "...", "pow_nonce": 123, "pow_difficulty": 4}`

### 2. Honeypot
- **Verify**: `POST /verify` with body `{"_hp_website": ""}`

### 3. Cap CAPTCHA
- **Proxy**: `ANY /cap-proxy/{path}`
- **Verify**: `POST /verify` with body `{"cap_token": "..."}`

## Integration Example

Your form backend should call this service before processing a submission:

```bash
curl -X POST https://your-cap-service.railway.app/verify \
     -H "Content-Type: application/json" \
     -d '{"cap_token": "user_token_here"}'
```
