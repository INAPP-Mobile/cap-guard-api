from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from urllib.parse import urljoin
import httpx

from app.config import settings
from app.captcha import generate_pow_challenge, verify_captcha

app = FastAPI(
    title="Cap CAPTCHA Service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/pow-challenge")
async def get_challenge(difficulty: int = None):
    return generate_pow_challenge(difficulty)

@app.post("/verify")
async def verify(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    
    # We can allow an optional secret key in the request for fine-grained control,
    # but typically we use the global settings.
    secret_key = body.get("site_secret_key")
    
    ok, err = await verify_captcha(body, secret_key)
    if ok:
        return {"success": True}
    return JSONResponse(status_code=400, content={"success": False, "error": err})

@app.api_route("/cap-proxy/{path:path}", methods=["GET", "POST", "OPTIONS", "HEAD"])
async def cap_proxy(path: str, request: Request):
    """Proxy requests to the Cap CAPTCHA service, adding CORS headers."""
    if not settings.cap_endpoint:
        return JSONResponse(status_code=503, content={"error": "CAP endpoint not configured"})
        
    target_url = urljoin(settings.cap_endpoint.rstrip("/") + "/", path)
    
    async with httpx.AsyncClient() as client:
        body = await request.body()
        resp = await client.request(
            method=request.method,
            url=target_url,
            content=body,
            headers={k: v for k, v in request.headers.items()
                     if k.lower() not in ("host", "content-length", "transfer-encoding", "connection")},
            params=request.query_params,
        )
        
    excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}
    return Response(content=resp.content, status_code=resp.status_code, headers=headers)
