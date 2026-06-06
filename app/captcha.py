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
    # A honeypot is "successful" (human) only if the field is NOT present 
    # OR if it is present but empty.
    # However, the bug was that it returned True too easily.
    # We should only ever return True for honeypot if it's the intended check.
    return data.get("_hp_website") == ""

async def verify_captcha(data: dict, cap_secret_key: Optional[str] = None) -> tuple[bool, Optional[str]]:
    # 1. Prioritize Cap Tokens (Strongest proof)
    cap_token = data.get("cap_token", data.get("cap-token", ""))
    if cap_token and settings.cap_endpoint and (cap_secret_key or settings.cap_secret_key):
        ok = await verify_cap(cap_token, cap_secret_key)
        if ok:
            return True, None

    # 2. Check PoW (Explicit computational proof)
    secret = data.get("pow_secret")
    nonce_str = data.get("pow_nonce")
    difficulty_str = data.get("pow_difficulty")
    
    if secret and nonce_str and difficulty_str:
        try:
            nonce = int(nonce_str)
            difficulty = int(difficulty_str)
            if _verify_pow(secret, nonce, difficulty):
                return True, None
        except (ValueError, TypeError):
            pass

    # 3. Honeypot (Fallback/Weakest proof)
    # Only verify honeypot if NO other specialized proof was attempted 
    # or if it is the only thing provided.
    if verify_honeypot(data):
        # If the user provided a cap_token or pow_secret that failed, 
        # we should NOT let them pass just because the honeypot is empty.
        has_cap = bool(cap_token)
        has_pow = bool(secret and nonce_str)
        
        if not has_cap and not has_pow:
            return True, None

    return False, "Verification failed: No valid human proof provided"

def generate_pow_challenge(difficulty: Optional[int] = None) -> dict:
    diff = difficulty or settings.pow_default_difficulty
    return _make_challenge(diff)
