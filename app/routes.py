"""Kohvilogi API endpoint'id — tegevused (lisamine, kustutamine, statistika).

Provides both HTML page routes and versioned JSON API endpoints under /api/v1/.
"""

from secrets import token_urlsafe
from typing import Optional

from fastapi import Request, Form, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from datetime import datetime, date, timedelta

from app.database import (
    get_db, add_expense, get_expenses, get_today_total,
    get_daily_summary, delete_expense, get_monthly_stats,
    get_world_stats,
)
from app.constants import COFFEE_TYPES, CURRENCIES, COUNTRY_SUGGESTIONS, COUNTRY_INFO, COFFEE_REGIONS
from app.auth import require_auth
from app.logging_config import get_logger

logger = get_logger("kohvilogi.routes")

VALID_COFFEE_TYPES = {
    "espresso", "americano", "cappuccino", "latte", "flat white",
    "macchiato", "mocha", "ristretto", "lungo", "cold brew",
    "filterkohv", "muu",
}
VALID_COUNTRIES = set(COUNTRY_INFO.keys())


def register_routes(app, templates):
    """Registreeri kõik endpoint'id FastAPI app'ile.

    Includes:
    - HTML pages: /, /stats, /map
    - JSON API (v1): /api/v1/stats, /api/v1/world, /api/v1/expenses, etc.
    - Utility: /health, /manifest.json, /sw.js
    """

    # ============================================================
    # HTML Pages
    # ============================================================

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Main dashboard page — shows today's coffees and quick stats."""
        if "csrf_token" not in request.session:
            request.session["csrf_token"] = token_urlsafe(32)
        today = datetime.now().strftime("%Y-%m-%d")
        expenses = get_expenses(date=today)
        totals = get_today_total()
        summary = get_daily_summary()
        all_expenses = get_expenses(limit=30)

        conn = get_db()
        total_drinks = conn.execute("SELECT COUNT(*) as cnt FROM expenses").fetchone()["cnt"]
        unique_countries = conn.execute("SELECT COUNT(DISTINCT country) as cnt FROM expenses WHERE country != ''").fetchone()["cnt"]
        conn.close()

        return templates.TemplateResponse(request, "index.html", {
            "expenses": expenses,
            "all_expenses": all_expenses,
            "totals": totals,
            "summary": summary,
            "total_drinks": total_drinks,
            "unique_countries": unique_countries,
            "coffee_types": COFFEE_TYPES,
            "currencies": CURRENCIES,
            "countries": COUNTRY_SUGGESTIONS,
            "csrf_token": request.session["csrf_token"],
        })

    @app.post("/add")
    async def add(
        request: Request,
        coffee_type: str = Form(...),
        amount: str = Form(...),
        currency: str = Form("EUR"),
        notes: str = Form(""),
        location: str = Form(""),
        country: str = Form(""),
        latitude: str = Form("0"),
        longitude: str = Form("0"),
    ):
        """Add a new coffee expense (HTML form submission)."""
        # CSRF validation
        form = await request.form()
        if form.get("csrf_token") != request.session.get("csrf_token"):
            return JSONResponse({"error": "Invalid CSRF token"}, status_code=403)

        # Input validation
        if coffee_type.lower().strip() not in VALID_COFFEE_TYPES:
            return RedirectResponse(url=f"/?error=Invalid coffee type: {coffee_type}", status_code=303)
        country_stripped = country.strip().upper() if country else ""
        if country_stripped and country_stripped not in VALID_COUNTRIES:
            return RedirectResponse(url=f"/?error=Invalid country code: {country}", status_code=303)

        try:
            amt = float(amount.replace(",", "."))
            lat = float(latitude) if latitude else 0
            lon = float(longitude) if longitude else 0
            add_expense(
                item=coffee_type, coffee_type=coffee_type, amount=amt,
                currency=currency.upper(), notes=notes,
                location=location, country=country.upper(),
                latitude=lat, longitude=lon,
            )
        except (ValueError, AttributeError):
            return RedirectResponse(url="/?error=Invalid amount format", status_code=303)
        return RedirectResponse(url="/", status_code=303)

    @app.post("/delete/{expense_id}")
    async def delete(expense_id: int):
        """Delete a coffee expense by ID."""
        # Check existence first
        conn = get_db()
        existing = conn.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,)).fetchone()
        if not existing:
            conn.close()
            return JSONResponse({"error": "Expense not found"}, status_code=404)
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        conn.close()
        return RedirectResponse(url="/", status_code=303)

    @app.get("/stats", response_class=HTMLResponse)
    async def stats(request: Request, month: str | None = None):
        """Monthly statistics page."""
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        data = get_monthly_stats(month)
        return templates.TemplateResponse(request, "stats.html", {
            "month": month,
            "data": data,
            "coffee_types": COFFEE_TYPES,
            "currencies": CURRENCIES,
        })

    @app.get("/map", response_class=HTMLResponse)
    async def world(request: Request):
        """World map page showing coffee travel history."""
        return templates.TemplateResponse(request, "world.html", {})

    # ============================================================
    # API v1 Endpoints (JSON)
    # ============================================================

    @app.get("/api/v1/expenses", dependencies=[Depends(require_auth)])
    async def api_v1_expenses(
        date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
        limit: int = Query(100, ge=1, le=1000, description="Max results"),
    ):
        """List coffee expenses with optional filtering."""
        expenses = get_expenses(date=date if date else None, limit=limit)
        return {"success": True, "count": len(expenses), "data": expenses}

    @app.post("/api/v1/expenses", dependencies=[Depends(require_auth)])
    async def api_v1_expenses_create(request: Request):
        """Create a new coffee expense via JSON API."""
        body = await request.json()

        coffee_type = body.get("coffee_type", "").strip().lower()
        if coffee_type not in VALID_COFFEE_TYPES:
            return JSONResponse(
                {"success": False, "error": f"Invalid coffee type. Allowed: {', '.join(sorted(VALID_COFFEE_TYPES))}"},
                status_code=400,
            )

        country = body.get("country", "").strip().upper()
        if country and country not in VALID_COUNTRIES:
            return JSONResponse(
                {"success": False, "error": f"Invalid country code: {country!r}"},
                status_code=400,
            )

        try:
            amount = float(body.get("amount", 0))
            if amount <= 0 or amount > 99999:
                raise ValueError("Amount out of range")
        except (ValueError, TypeError):
            return JSONResponse(
                {"success": False, "error": "Amount must be a positive number up to 99999"},
                status_code=400,
            )

        rowid = add_expense(
            item=coffee_type,
            coffee_type=coffee_type,
            amount=amount,
            currency=body.get("currency", "EUR").upper(),
            notes=body.get("notes", ""),
            location=body.get("location", ""),
            country=country,
            latitude=float(body.get("latitude", 0)),
            longitude=float(body.get("longitude", 0)),
        )

        logger.info(f"Coffee expense created via API: id={rowid}")
        return JSONResponse(
            {"success": True, "id": rowid, "message": "Expense created"},
            status_code=201,
        )

    @app.post("/api/v1/expenses/{expense_id}", dependencies=[Depends(require_auth)])
    async def api_v1_expenses_delete(expense_id: int):
        """Delete a coffee expense by ID (JSON API)."""
        deleted = delete_expense(expense_id)
        if not deleted:
            return JSONResponse(
                {"success": False, "error": "Expense not found"},
                status_code=404,
            )
        return {"success": True, "message": f"Expense {expense_id} deleted"}

    @app.get("/api/v1/stats", dependencies=[Depends(require_auth)])
    async def api_stats():
        """Dashboard statistics: streak, totals, progress."""
        conn = get_db()

        # Streak: consecutive days with at least one coffee
        streak = 0
        check_date = date.today()
        while True:
            rows = conn.execute(
                "SELECT COUNT(*) as cnt FROM expenses WHERE date = ?",
                (check_date.strftime("%Y-%m-%d"),)
            ).fetchone()
            if rows and rows["cnt"] > 0:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        total = conn.execute("SELECT COUNT(*) as cnt FROM expenses").fetchone()["cnt"]
        countries = conn.execute(
            "SELECT COUNT(DISTINCT country) as cnt FROM expenses WHERE country != ''"
        ).fetchone()["cnt"]
        first = conn.execute("SELECT MIN(date) as d FROM expenses").fetchone()["d"]
        days_since = None
        if first:
            days_since = (date.today() - date.fromisoformat(first)).days + 1

        week_start = (date.today() - timedelta(days=date.today().weekday())).strftime("%Y-%m-%d")
        week_drinks = conn.execute(
            "SELECT COUNT(*) as cnt FROM expenses WHERE date >= ?", (week_start,)
        ).fetchone()["cnt"]

        conn.close()

        return {
            "streak": streak,
            "total_drinks": total,
            "unique_countries": countries,
            "days_since_first": days_since,
            "week_drinks": week_drinks,
            "world_progress": round(countries / 195 * 100, 1) if countries else 0,
        }

    @app.get("/api/v1/world")
    async def api_world():
        """JSON API for coffee map data with country flags and regions."""
        data = get_world_stats()
        for c in data["countries"]:
            info = COUNTRY_INFO.get(c["country"], {})
            c["flag"] = info.get("flag", "🏳️")
            c["country_name"] = info.get("name", c["country"])
        for p in data["passport"]:
            info = COUNTRY_INFO.get(p["country"], {})
            p["flag"] = info.get("flag", "🏳️")
            p["country_name"] = info.get("name", p["country"])
        data["regions"] = COFFEE_REGIONS
        return data

    @app.get("/api/v1/world/top3")
    async def api_world_top3():
        """Top 3 coffee types per country."""
        conn = get_db()
        rows = conn.execute("""
            SELECT country, coffee_type, COUNT(*) as cnt
            FROM expenses
            WHERE country != '' AND coffee_type != ''
            GROUP BY country, coffee_type
            ORDER BY country, cnt DESC
        """).fetchall()
        conn.close()

        result = {}
        for r in rows:
            cc = r["country"]
            if cc not in result:
                result[cc] = []
            if len(result[cc]) < 3:
                result[cc].append({"type": r["coffee_type"], "count": r["cnt"]})

        for cc in result:
            info = COUNTRY_INFO.get(cc, {})
            result[cc] = {
                "coffees": result[cc],
                "flag": info.get("flag", "🏳️"),
                "country_name": info.get("name", cc),
            }

        return result

    @app.get("/api/v1/world/by-year")
    async def api_world_by_year():
        """Coffee counts by year and country."""
        conn = get_db()
        rows = conn.execute("""
            SELECT strftime('%Y', date) as year, country, COUNT(*) as cnt
            FROM expenses
            WHERE country != ''
            GROUP BY year, country
            ORDER BY year, cnt DESC
        """).fetchall()
        conn.close()

        result = {}
        for r in rows:
            y = r["year"]
            if y not in result:
                result[y] = {"countries": [], "total": 0}
            result[y]["countries"].append({
                "country": r["country"],
                "count": r["cnt"],
                **COUNTRY_INFO.get(r["country"], {"flag": "🏳️", "name": r["country"]}),
            })
            result[y]["total"] += r["cnt"]

        return result

    @app.get("/api/v1/share")
    async def api_share():
        """Shareable summary for QR code / link."""
        stats_data = await api_stats()
        import json
        from base64 import b64encode
        payload = b64encode(json.dumps(stats_data).encode()).decode()
        return {
            **stats_data,
            "share_url": f"/share/{payload}",
            "text": f"☕ Kohvilogi: {stats_data['total_drinks']} kohvi, {stats_data['unique_countries']} riiki, {stats_data['streak']} päeva streak!",
        }

    # ============================================================
    # Backward-compatible (unversioned) API routes
    # ============================================================

    @app.get("/api/stats")
    async def api_stats_unversioned():
        """Legacy endpoint — redirects to v1 data."""
        return await api_stats()

    @app.get("/api/world")
    async def api_world_unversioned():
        """Legacy endpoint — redirects to v1 data."""
        return await api_world()

    @app.get("/api/world/top3")
    async def api_world_top3_unversioned():
        """Legacy endpoint — redirects to v1 data."""
        return await api_world_top3()

    @app.get("/api/world/by-year")
    async def api_world_by_year_unversioned():
        """Legacy endpoint — redirects to v1 data."""
        return await api_world_by_year()

    @app.get("/api/share")
    async def api_share_unversioned():
        """Legacy endpoint — redirects to v1 data."""
        return await api_share()

    # ============================================================
    # PWA & Utility endpoints
    # ============================================================

    @app.get("/manifest.json")
    async def manifest():
        """PWA Web App Manifest."""
        return {
            "name": "Kohvilogi",
            "short_name": "Kohvilogi",
            "description": "Kohvilogi — jälgige kohvi maailmas",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#111827",
            "theme_color": "#065f46",
            "orientation": "portrait-primary",
            "icons": [
                {"src": "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/2615.svg", "sizes": "any", "type": "image/svg+xml"}
            ],
            "categories": ["food", "lifestyle"],
            "lang": "et",
        }

    @app.get("/sw.js", response_class=HTMLResponse)
    async def service_worker():
        """Service Worker for offline PWA support."""
        js = """
const CACHE = 'kohvilogi-v1';
const ASSETS = ['/', '/map', '/stats', '/manifest.json'];

self.addEventListener('install', e => {
    e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
    self.skipWaiting();
});

self.addEventListener('activate', e => {
    e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))));
    self.clients.claim();
});

self.addEventListener('fetch', e => {
    if (e.request.method !== 'GET') return;
    e.respondWith(
        caches.match(e.request).then(cached => {
            const fetched = fetch(e.request).then(response => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE).then(c => c.put(e.request, clone));
                }
                return response;
            }).catch(() => cached);
            return cached || fetched;
        })
    );
});"""
        return HTMLResponse(content=js, media_type="application/javascript")
