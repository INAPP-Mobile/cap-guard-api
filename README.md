# Cap CAPTCHA Template

Standalone CAPTCHA service for web forms, providing Proof-of-Work (PoW), Honeypot, and Proxy services for external CAPTCHA providers.

## 🚀 Deployment on Railway

This project is optimized for Railway. 

### One-Click Deploy
If you see a "Deploy to Railway" button, click it to get started. Otherwise:
1. Create a new project on [Railway](https://railway.app).
2. Connect this GitHub repository.
3. Railway will automatically detect the `railway.toml` and deploy the service.

### Environment Variables
Configure the following variables in the Railway dashboard:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `CAP_ENDPOINT` | The URL of the underlying Cap CAPTCHA service | Required |
| `CAP_SECRET_KEY` | The secret key for Cap verification | Required |
| `POW_DEFAULT_DIFFICULTY` | Default difficulty for PoW challenges | `4` |

## ✨ Features

- **PoW Challenges**: Request a computational challenge to thwart simple bots.
- **Honeypot Verification**: Simple check for hidden fields.
- **Cap Proxy**: CORS-enabled proxy for the Cap CAPTCHA service.
- **Unified Verification API**: One endpoint to verify different types of human proof.

## 🛠 API Usage

### 1. Proof-of-Work (PoW)
- **Request Challenge**: `GET /pow-challenge?difficulty=4`
- **Verify**: `POST /verify` with body:
  ```json
  {
    "pow_secret": "...", 
    "pow_nonce": 123, 
    "pow_difficulty": 4
  }
  ```

### 2. Honeypot
- **Verify**: `POST /verify` with body:
  ```json
  {
    "_hp_website": ""
  }
  ```

### 3. Cap CAPTCHA
- **Proxy**: `ANY /cap-proxy/{path}`
- **Verify**: `POST /verify` with body:
  ```json
  {
    "cap_token": "..."
  }
  ```

## 🔗 Integration Example

Your form backend should call this service before processing a submission:

```bash
curl -X POST https://your-cap-service.railway.app/verify \
     -H "Content-Type: application/json" \
     -d '{"cap_token": "user_token_here"}'
```
