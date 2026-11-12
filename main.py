import os, json, secrets
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, String, Float, DateTime, Boolean, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from itsdangerous import URLSafeSerializer, BadSignature
from passlib.context import CryptContext
import urllib.request

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class Quote(Base):
    __tablename__ = "quotes"
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    price: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(40))
    lot_size: Mapped[str] = mapped_column(String(40))
    currency: Mapped[str] = mapped_column(String(8))
    source: Mapped[str] = mapped_column(String(40), default="Illustrative")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_illustrative: Mapped[bool] = mapped_column(Boolean, default=True)

Base.metadata.create_all(engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeSerializer(os.getenv("APP_SECRET_KEY", "unsafe-development-key-change-me"))
app = FastAPI(title="Prosper Vista Research")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

SEED = [
    ("MCX_GOLD", "MCX Gold", 138700.0, "INR / 10 grams", "100 grams", "INR"),
    ("MCX_SILVER", "MCX Silver", 182500.0, "INR / kg", "30 kg", "INR"),
    ("XAUUSD", "Spot Gold (XAUUSD)", 4000.0, "USD / troy ounce", "Spot", "USD"),
    ("XAGUSD", "Spot Silver (XAGUSD)", 51.0, "USD / troy ounce", "Spot", "USD"),
]
with SessionLocal() as db:
    for symbol, name, price, unit, lot, currency in SEED:
        if not db.get(Quote, symbol):
            db.add(Quote(symbol=symbol, name=name, price=price, unit=unit, lot_size=lot,
                         currency=currency, source="Illustrative starting value", is_illustrative=True))
    db.commit()

def is_admin(request: Request) -> bool:
    token = request.cookies.get("pvr_admin")
    if not token:
        return False
    try:
        payload = serializer.loads(token)
        return payload.get("admin") is True
    except BadSignature:
        return False

def require_admin(request: Request):
    if not is_admin(request):
        raise HTTPException(status_code=401, detail="Admin login required")

def get_quotes():
    with SessionLocal() as db:
        return list(db.scalars(select(Quote).order_by(Quote.symbol)))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    from fastapi.templating import Jinja2Templates
    return templates.TemplateResponse("index.html", {"request": request})

templates = Jinja2Templates(directory="app/static")

@app.get("/api/quotes")
def api_quotes():
    result = []
    for q in get_quotes():
        result.append({
            "symbol": q.symbol, "name": q.name, "price": q.price, "unit": q.unit,
            "lot_size": q.lot_size, "currency": q.currency, "source": q.source,
            "updated_at": q.updated_at.isoformat() if q.updated_at else None,
            "illustrative": q.is_illustrative
        })
    return result

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    if not is_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    return templates.TemplateResponse("admin.html", {"request": request, "quotes": get_quotes()})

@app.get("/admin/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})

@app.post("/admin/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    expected_user = os.getenv("ADMIN_USERNAME", "admin")
    password_hash = os.getenv("ADMIN_PASSWORD_HASH", "")
    if not password_hash or password_hash == "PASTE_BCRYPT_HASH_HERE":
        return templates.TemplateResponse("login.html", {"request": request, "error": "Admin password hash is not configured. Set ADMIN_PASSWORD_HASH in .env."}, status_code=503)
    if not secrets.compare_digest(username, expected_user) or not pwd_context.verify(password, password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password."}, status_code=401)
    response = RedirectResponse("/admin", status_code=303)
    response.set_cookie("pvr_admin", serializer.dumps({"admin": True}), httponly=True,
                        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
                        samesite="strict", max_age=8*60*60)
    return response

@app.post("/admin/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("pvr_admin")
    return response

@app.post("/api/admin/quote")
def update_quote(request: Request, symbol: str = Form(...), price: float = Form(...), source: str = Form("Manual admin update")):
    require_admin(request)
    if price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than zero")
    with SessionLocal() as db:
        q = db.get(Quote, symbol)
        if not q:
            raise HTTPException(status_code=404, detail="Unknown symbol")
        q.price = price
        q.source = source[:40]
        q.updated_at = datetime.now(timezone.utc)
        q.is_illustrative = False
        db.commit()
    return RedirectResponse("/admin", status_code=303)

@app.post("/api/admin/live-sync")
def live_sync(request: Request):
    require_admin(request)
    api_url = os.getenv("LIVE_PRICE_API_URL", "").strip()
    if not api_url:
        raise HTTPException(status_code=400, detail="Configure a licensed provider URL in .env before enabling live sync.")
    headers = {}
    api_key = os.getenv("LIVE_PRICE_API_KEY", "")
    if api_key:
        header = os.getenv("LIVE_PRICE_API_KEY_HEADER", "Authorization")
        prefix = os.getenv("LIVE_PRICE_API_KEY_PREFIX", "Bearer")
        headers[header] = f"{prefix} {api_key}".strip()
    req = urllib.request.Request(api_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
        # Expected normalized JSON: {"MCX_GOLD":138700,"MCX_SILVER":182500,"XAUUSD":4000,"XAGUSD":51}
        with SessionLocal() as db:
            for symbol, value in payload.items():
                q = db.get(Quote, symbol)
                if q and isinstance(value, (int, float)) and value > 0:
                    q.price = float(value)
                    q.source = "Live API"
                    q.updated_at = datetime.now(timezone.utc)
                    q.is_illustrative = False
            db.commit()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Live provider request failed: {type(exc).__name__}")
    return RedirectResponse("/admin", status_code=303)
