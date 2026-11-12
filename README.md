# Prosper Vista Research — deployable starter

A responsive commodity-research website with MCX and global spot quote cards, chart preview, daily research/service sections, protected admin login, manual price updates, and a generic live-provider adapter.

## Important market-data notes
- Initial prices are **illustrative values supplied by the site owner**, not verified live quotes:
  - MCX Gold: ₹138,700 per 10 g; contract lot shown as 100 g.
  - MCX Silver: ₹182,500 per kg; contract lot shown as 30 kg.
  - XAUUSD: approximately $4,000 per troy ounce.
  - XAGUSD: approximately $51 per troy ounce (within the supplied $50–52 range).
- Verify the active MCX contract's exact unit, lot size, expiry and quote convention before publishing.
- XAUUSD/XAGUSD are spot-market symbols; COMEX futures are separate instruments (commonly GC and SI). Do not label spot quotes as COMEX futures.
- The chart currently shows **sample illustrative history**, not actual historical prices.
- A licensed data vendor and API credentials are required for genuine real-time prices. MCX data licensing/redistribution permissions may apply.

## 1. Configure secrets
```bash
cp .env.example .env
```
Generate strong passwords and an app secret. Generate a bcrypt hash for the admin password:
```bash
docker run --rm python:3.12-slim sh -c "pip install passlib[bcrypt] && python -c 'from passlib.context import CryptContext; print(CryptContext(schemes=[\"bcrypt\"]).hash(\"YOUR-STRONG-ADMIN-PASSWORD\"))'"
```
Paste the hash into `ADMIN_PASSWORD_HASH`. Replace all `CHANGE_ME` values. Ensure `DATABASE_URL` password matches `MYSQL_PASSWORD`.

## 2. Deploy
```bash
docker compose up -d --build
docker compose ps
docker compose logs -f web
```
Open `http://YOUR_VM_EXTERNAL_IP:8082`. Admin: `/admin/login`.

## 3. GCP firewall
Create/verify an ingress allow rule for TCP `8082` targeted to the VM's network tag. For safer testing, set source IPv4 range to your own public IP `/32` rather than `0.0.0.0/0`. Do not open MySQL port 3306 publicly. If you later put Nginx in front, expose 80/443 and keep app port private.

## 4. Live provider adapter
Set `LIVE_PRICE_API_URL`, `LIVE_PRICE_API_KEY`, and header/prefix in `.env`. The endpoint must return normalized JSON:
```json
{
  "MCX_GOLD": 138700,
  "MCX_SILVER": 182500,
  "XAUUSD": 4000,
  "XAGUSD": 51.25
}
```
Then restart:
```bash
docker compose up -d
```
Admin → Sync live prices. Provider-specific response mapping may need a small adapter change. Never scrape or redistribute exchange data without checking provider/exchange terms.

## 5. Security before public launch
- Use HTTPS and a domain; set `COOKIE_SECURE=true` once HTTPS is configured.
- Use a long unique admin password and app secret; do not commit `.env` to GitHub.
- Restrict admin access by IP/VPN where practical; add rate limiting and audit logging before production.
- Back up the MySQL volume.
- Add a real licensed quote feed, real historical OHLC data, and timestamp/source labels.
- Add daily reports only after the research content is reviewed and dated.

## Current scope
This is a functional starter project, not a fully audited financial-services platform. It does not provide personalized investment advice, guaranteed predictions, broker execution, or live prices until a provider is configured.
