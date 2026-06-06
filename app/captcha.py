import hashlib
import secrets
from typing import Optional
from urllib.parse import urljoin
import httpx
from app.config import settings

def _make_challenge(difficulty: int = 4) -> dict:
    secret = secrets.token_hex(16)
    prefix = "0" * difficulty
    nonce = 0
    while True:
        candidate = f"{secret}{nonce}"
        h = hashlib.sha256(candidate.encode()).hexdigest()
        if h.startswith(prefix):
            return {"secret": secret, "nonce": nonce, "difficulty": difficulty}
        nonce += 1

def _verify_pow(secret: str, nonce: int, difficulty: int) -> bool:
    candidate = f"{secret}{nonce}"
    h = hashlib.sha256(candidate.encode()).hexdigest()
    return h.startswith("0" * difficulty)

async def verify_cap(token: str, secret_key: Optional[str] = None) -> bool:
    secret = secret_key or settings.cap_secret_key
    if not settings.cap_endpoint or not secret:
        return False
    url = urljoin(settings.cap_endpoint.rstrip("/") + "/", "siteverify")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                url,
                json={"secret": secret, "response": token},
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("success", False)
    except (httpx.RequestError, ValueError):
        pass
    return False

def verify_honeypot(data: dict) -> bool:
    hp = data.get("_hp_website", "")
    return hp == ""

async def verify_captcha(data: dict, cap_secret_key: Optional[str] = None) -> tuple[bool, Optional[str]]:
    # This is a simplified version of the logic from railway-form-template
    # It attempts to verify based on provided fields
    
    cap_token = data.get("cap_token", data.get("cap-token", ""))
    if cap_token and settings.cap_endpoint and (cap_secret_key or settings.cap_secret_key):
        ok = await verify_cap(cap_token, cap_secret_key)
        if ok:
            return True, None

    if verify_honeypot(data):
        # Note: Honeypot is positive if EMPTY. 
        # In a real-world consolidated verify, we might need a flag to know if it's the only check.
        # For a dedicated API, we can treat a valid honeypot as a fallback "success" 
        # if nothing else matches, or provide separate endpoints.
        # Let's stick to the logic: if honeypot field is empty, it's "human-like" behavior.
        return True, None

    # PoW check
    secret = data.get("pow_secret", "")
    nonce_str = data.get("pow_nonce", "0")
    difficulty_str = data.get("pow_difficulty", "4")
    try:
        nonce = int(nonce_str)
        difficulty = int(difficulty_str)
    except (ValueError, TypeError):
        pass
    else:
        if _verify_pow(secret, nonce, difficulty):
            return True, None

    return False, "Verification failed: No valid human proof provided"

def generate_pow_challenge(difficulty: Optional[int] = None) -> dict:
    diff = difficulty or settings.pow_default_difficulty
    return _make_challenge(diff)
