import logging
import time
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from contextlib import asynccontextmanager
from app.database.mongodb import mongodb
from app.routes import reports, diet
from app.routes.auth import router as auth_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CRIT-4: Simple in-memory rate limiter for auth endpoints
# ---------------------------------------------------------------------------
class _RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._store: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        times = [t for t in self._store[key] if t > cutoff]
        if len(times) >= self.max_requests:
            self._store[key] = times
            return False
        times.append(now)
        self._store[key] = times
        return True


_auth_limiter = _RateLimiter(max_requests=10, window_seconds=60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb.connect()
    yield
    await mongodb.disconnect()


app = FastAPI(
    title="Dietician Agent API",
    version="2.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# MED-1: Explicit CORS — no wildcard methods/headers
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ---------------------------------------------------------------------------
# HIGH-5: Security response headers on every response
# ---------------------------------------------------------------------------
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    # CSP: API only serves JSON; no scripts/frames needed
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response


# ---------------------------------------------------------------------------
# CRIT-4: Rate-limit /api/auth/* endpoints
# ---------------------------------------------------------------------------
@app.middleware("http")
async def rate_limit_auth(request: Request, call_next):
    if request.url.path.startswith("/api/auth/login") or request.url.path.startswith("/api/auth/register"):
        client_ip = request.client.host if request.client else "unknown"
        if not _auth_limiter.is_allowed(client_ip):
            logger.warning("Rate limit exceeded for IP=%s on %s", client_ip, request.url.path)
            raise HTTPException(status_code=429, detail="Too many requests — please wait and try again")
    return await call_next(request)


app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(reports.router, prefix="/api/reports", tags=["Lab Reports"])
app.include_router(diet.router, prefix="/api/diet", tags=["Diet Plans"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
