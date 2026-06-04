from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from app.database import (
    init_db, add_expense, get_expenses, get_today_total,
    get_daily_summary, delete_expense, get_monthly_stats,
    get_world_stats, upsert_coffee_country, get_coffee_countries,
)

app = FastAPI(title="Kohvilogi")
templates = Jinja2Templates(directory="templates")

init_db()

COFFEE_TYPES = [
    "Espresso", "Americano", "Cappuccino", "Latte", "Flat White",
    "Macchiato", "Mocha", "Ristretto", "Lungo", "Cold Brew",
    "Filterkohv", "Muu",
]

CURRENCIES = [
    ("EUR", "€"), ("USD", "$"), ("GBP", "£"),
    ("SEK", "kr"), ("NOK", "kr"), ("DKK", "kr"),
    ("CHF", "Fr"), ("JPY", "¥"), ("TRY", "₺"),
    ("AUD", "A$"), ("CAD", "C$"), ("NZD", "NZ$"),
]

# Common country suggestions for autocomplete
COUNTRY_SUGGESTIONS = [
    ("EE", "Eesti", "🇪🇪"), ("FI", "Soome", "🇫🇮"), ("LV", "Läti", "🇱🇻"),
    ("LT", "Leedu", "🇱🇹"), ("SE", "Rootsi", "🇸🇪"), ("NO", "Norra", "🇳🇴"),
    ("DK", "Taani", "🇩🇰"), ("DE", "Saksamaa", "🇩🇪"), ("NL", "Holland", "🇳🇱"),
    ("BE", "Belgia", "🇧🇪"), ("FR", "Prantsusmaa", "🇫🇷"), ("ES", "Hispaania", "🇪🇸"),
    ("PT", "Portugal", "🇵🇹"), ("IT", "Itaalia", "🇮🇹"), ("AT", "Austria", "🇦🇹"),
    ("CH", "Šveits", "🇨🇭"), ("PL", "Poola", "🇵🇱"), ("CZ", "Tšehhi", "🇨🇿"),
    ("HU", "Ungari", "🇭🇺"), ("RO", "Rumeenia", "🇷🇴"), ("BG", "Bulgaaria", "🇧🇬"),
    ("GR", "Kreeka", "🇬🇷"), ("TR", "Türgi", "🇹🇷"), ("GB", "Suurbritannia", "🇬🇧"),
    ("IE", "Iirimaa", "🇮🇪"), ("US", "USA", "🇺🇸"), ("CA", "Kanada", "🇨🇦"),
    ("MX", "Mehhiko", "🇲🇽"), ("BR", "Brasiilia", "🇧🇷"), ("AR", "Argentina", "🇦🇷"),
    ("CO", "Colombia", "🇨🇴"), ("ET", "Etioopia", "🇪🇹"), ("KE", "Keenia", "🇰🇪"),
    ("JP", "Jaapan", "🇯🇵"), ("CN", "Hiina", "🇨🇳"), ("TH", "Tai", "🇹🇭"),
    ("VN", "Vietnam", "🇻🇳"), ("ID", "Indoneesia", "🇮🇩"), ("AU", "Austraalia", "🇦🇺"),
    ("NZ", "Uus-Meremaa", "🇳🇿"), ("AE", "Araabia Ühendemiraadid", "🇦🇪"),
    ("IN", "India", "🇮🇳"), ("CR", "Costa Rica", "🇨🇷"), ("GT", "Guatemala", "🇬🇹"),
]

# Full country code -> flag + name mapping for passport display
COUNTRY_INFO = {
    "EE": {"name": "Eesti", "flag": "🇪🇪"}, "FI": {"name": "Soome", "flag": "🇫🇮"},
    "LV": {"name": "Läti", "flag": "🇱🇻"}, "LT": {"name": "Leedu", "flag": "🇱🇹"},
    "SE": {"name": "Rootsi", "flag": "🇸🇪"}, "NO": {"name": "Norra", "flag": "🇳🇴"},
    "DK": {"name": "Taani", "flag": "🇩🇰"}, "DE": {"name": "Saksamaa", "flag": "🇩🇪"},
    "NL": {"name": "Holland", "flag": "🇳🇱"}, "BE": {"name": "Belgia", "flag": "🇧🇪"},
    "FR": {"name": "Prantsusmaa", "flag": "🇫🇷"}, "ES": {"name": "Hispaania", "flag": "🇪🇸"},
    "PT": {"name": "Portugal", "flag": "🇵🇹"}, "IT": {"name": "Itaalia", "flag": "🇮🇹"},
    "AT": {"name": "Austria", "flag": "🇦🇹"}, "CH": {"name": "Šveits", "flag": "🇨🇭"},
    "PL": {"name": "Poola", "flag": "🇵🇱"}, "CZ": {"name": "Tšehhi", "flag": "🇨🇿"},
    "HU": {"name": "Ungari", "flag": "🇭🇺"}, "RO": {"name": "Rumeenia", "flag": "🇷🇴"},
    "BG": {"name": "Bulgaaria", "flag": "🇧🇬"}, "GR": {"name": "Kreeka", "flag": "🇬🇷"},
    "TR": {"name": "Türgi", "flag": "🇹🇷"}, "GB": {"name": "Suurbritannia", "flag": "🇬🇧"},
    "IE": {"name": "Iirimaa", "flag": "🇮🇪"}, "US": {"name": "USA", "flag": "🇺🇸"},
    "CA": {"name": "Kanada", "flag": "🇨🇦"}, "MX": {"name": "Mehhiko", "flag": "🇲🇽"},
    "BR": {"name": "Brasiilia", "flag": "🇧🇷"}, "AR": {"name": "Argentina", "flag": "🇦🇷"},
    "CO": {"name": "Colombia", "flag": "🇨🇴"}, "ET": {"name": "Etioopia", "flag": "🇪🇹"},
    "KE": {"name": "Keenia", "flag": "🇰🇪"}, "JP": {"name": "Jaapan", "flag": "🇯🇵"},
    "CN": {"name": "Hiina", "flag": "🇨🇳"}, "TH": {"name": "Tai", "flag": "🇹🇭"},
    "VN": {"name": "Vietnam", "flag": "🇻🇳"}, "ID": {"name": "Indoneesia", "flag": "🇮🇩"},
    "AU": {"name": "Austraalia", "flag": "🇦🇺"}, "NZ": {"name": "Uus-Meremaa", "flag": "🇳🇿"},
    "AE": {"name": "AÜE", "flag": "🇦🇪"}, "IN": {"name": "India", "flag": "🇮🇳"},
    "CR": {"name": "Costa Rica", "flag": "🇨🇷"}, "GT": {"name": "Guatemala", "flag": "🇬🇹"},
    "IS": {"name": "Island", "flag": "🇮🇸"}, "UA": {"name": "Ukraina", "flag": "🇺🇦"},
    "RU": {"name": "Venemaa", "flag": "🇷🇺"}, "ZA": {"name": "Lõuna-Aafrika", "flag": "🇿🇦"},
    "EG": {"name": "Egiptus", "flag": "🇪🇬"}, "MA": {"name": "Maroko", "flag": "🇲🇦"},
    "KR": {"name": "Lõuna-Korea", "flag": "🇰🇷"}, "TW": {"name": "Taiwan", "flag": "🇹🇼"},
    "MY": {"name": "Malaisia", "flag": "🇲🇾"}, "PH": {"name": "Filipiinid", "flag": "🇵🇭"},
    "PE": {"name": "Peruu", "flag": "🇵🇪"}, "EC": {"name": "Ecuador", "flag": "🇪🇨"},
    "HN": {"name": "Honduras", "flag": "🇭🇳"}, "NI": {"name": "Nicaragua", "flag": "🇳🇮"},
    "PA": {"name": "Panama", "flag": "🇵🇦"}, "JM": {"name": "Jamaica", "flag": "🇯🇲"},
    "HT": {"name": "Haiti", "flag": "🇭🇹"}, "DO": {"name": "Dominikaani", "flag": "🇩🇴"},
    "CU": {"name": "Kuuba", "flag": "🇨🇺"}, "SK": {"name": "Slovakkia", "flag": "🇸🇰"},
    "SI": {"name": "Sloveenia", "flag": "🇸🇮"}, "HR": {"name": "Horvaatia", "flag": "🇭🇷"},
    "RS": {"name": "Serbia", "flag": "🇷🇸"}, "BA": {"name": "Bosnia", "flag": "🇧🇦"},
    "ME": {"name": "Montenegro", "flag": "🇲🇪"}, "MK": {"name": "Põhja-Makedoonia", "flag": "🇲🇰"},
    "AL": {"name": "Albaania", "flag": "🇦🇱"}, "XK": {"name": "Kosovo", "flag": "🇽🇰"},
    "MT": {"name": "Malta", "flag": "🇲🇹"}, "CY": {"name": "Küpros", "flag": "🇨🇾"},
    "LU": {"name": "Luksemburg", "flag": "🇱🇺"}, "LI": {"name": "Liechtenstein", "flag": "🇱🇮"},
    "MC": {"name": "Monaco", "flag": "🇲🇨"}, "AD": {"name": "Andorra", "flag": "🇦🇩"},
    "SM": {"name": "San Marino", "flag": "🇸🇲"}, "VA": {"name": "Vatikan", "flag": "🇻🇦"},
    "BY": {"name": "Valgevene", "flag": "🇧🇾"}, "MD": {"name": "Moldova", "flag": "🇲🇩"},
    "GE": {"name": "Gruusia", "flag": "🇬🇪"}, "AM": {"name": "Armeenia", "flag": "🇦🇲"},
    "AZ": {"name": "Aserbaidžaan", "flag": "🇦🇿"}, "KZ": {"name": "Kasahstan", "flag": "🇰🇿"},
    "UZ": {"name": "Usbekistan", "flag": "🇺🇿"}, "KG": {"name": "Kõrgõzstan", "flag": "🇰🇬"},
    "TJ": {"name": "Tadžikistan", "flag": "🇹🇯"}, "MN": {"name": "Mongoolia", "flag": "🇲🇳"},
    "KP": {"name": "Põhja-Korea", "flag": "🇰🇵"}, "LK": {"name": "Sri Lanka", "flag": "🇱🇰"},
    "BD": {"name": "Bangladesh", "flag": "🇧🇩"}, "NP": {"name": "Nepal", "flag": "🇳🇵"},
    "MM": {"name": "Myanmar", "flag": "🇲🇲"}, "LA": {"name": "Laos", "flag": "🇱🇦"},
    "KH": {"name": "Kambodža", "flag": "🇰🇭"}, "BN": {"name": "Brunei", "flag": "🇧🇳"},
    "SG": {"name": "Singapur", "flag": "🇸🇬"}, "HK": {"name": "Hongkong", "flag": "🇭🇰"},
    "MO": {"name": "Macau", "flag": "🇲🇴"}, "PK": {"name": "Pakistan", "flag": "🇵🇰"},
    "AF": {"name": "Afganistan", "flag": "🇦🇫"}, "IR": {"name": "Iraan", "flag": "🇮🇷"},
    "IQ": {"name": "Iraak", "flag": "🇮🇶"}, "SY": {"name": "Süüria", "flag": "🇸🇾"},
    "JO": {"name": "Jordaania", "flag": "🇯🇴"}, "LB": {"name": "Liibanon", "flag": "🇱🇧"},
    "IL": {"name": "Iisrael", "flag": "🇮🇱"}, "PS": {"name": "Palestiina", "flag": "🇵🇸"},
    "SA": {"name": "Saudi Araabia", "flag": "🇸🇦"}, "YE": {"name": "Jeemen", "flag": "🇾🇪"},
    "OM": {"name": "Omaan", "flag": "🇴🇲"}, "QA": {"name": "Katar", "flag": "🇶🇦"},
    "BH": {"name": "Bahrein", "flag": "🇧🇭"}, "KW": {"name": "Kuveit", "flag": "🇰🇼"},
    "NG": {"name": "Nigeeria", "flag": "🇳🇬"}, "GH": {"name": "Ghana", "flag": "🇬🇭"},
    "CI": {"name": "Côte d'Ivoire", "flag": "🇨🇮"}, "SN": {"name": "Senegal", "flag": "🇸🇳"},
    "CM": {"name": "Kamerun", "flag": "🇨🇲"}, "CD": {"name": "Kongo DV", "flag": "🇨🇩"},
    "UG": {"name": "Uganda", "flag": "🇺🇬"}, "TZ": {"name": "Tansaania", "flag": "🇹🇿"},
    "RW": {"name": "Rwanda", "flag": "🇷🇼"}, "ET": {"name": "Etioopia", "flag": "🇪🇹"},
    "ZM": {"name": "Sambia", "flag": "🇿🇲"}, "ZW": {"name": "Zimbabwe", "flag": "🇿🇼"},
    "MW": {"name": "Malawi", "flag": "🇲🇼"}, "MZ": {"name": "Mosambiik", "flag": "🇲🇿"},
    "MG": {"name": "Madagaskar", "flag": "🇲🇬"}, "MU": {"name": "Mauritius", "flag": "🇲🇺"},
    "SC": {"name": "Seišellid", "flag": "🇸🇨"}, "CV": {"name": "Roheneemesaared", "flag": "🇨🇻"},
    "CL": {"name": "Tšiili", "flag": "🇨🇱"}, "PY": {"name": "Paraguay", "flag": "🇵🇾"},
    "UY": {"name": "Uruguay", "flag": "🇺🇾"}, "BO": {"name": "Boliivia", "flag": "🇧🇴"},
    "GY": {"name": "Guyana", "flag": "🇬🇾"}, "SR": {"name": "Suriname", "flag": "🇸🇷"},
    "VE": {"name": "Venezuela", "flag": "🇻🇪"}, "TT": {"name": "Trinidad", "flag": "🇹🇹"},
    "BB": {"name": "Barbados", "flag": "🇧🇧"}, "BS": {"name": "Bahama", "flag": "🇧🇸"},
    "IS": {"name": "Island", "flag": "🇮🇸"}, "FO": {"name": "Fääri saared", "flag": "🇫🇴"},
    "GL": {"name": "Gröönimaa", "flag": "🇬🇱"}, "SJ": {"name": "Svalbard", "flag": "🇸🇯"},
}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    today = datetime.now().strftime("%Y-%m-%d")
    expenses = get_expenses(date=today)
    totals = get_today_total()
    summary = get_daily_summary()

    # All expenses for history (last 30)
    all_expenses = get_expenses(limit=30)

    # Quick stats
    from app.database import get_db as _db
    conn = _db()
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
    })


@app.post("/add")
async def add(
    coffee_type: str = Form(...),
    amount: str = Form(...),
    currency: str = Form("EUR"),
    notes: str = Form(""),
    location: str = Form(""),
    country: str = Form(""),
    latitude: str = Form("0"),
    longitude: str = Form("0"),
):
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
    except ValueError:
        pass
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{expense_id}")
async def delete(expense_id: int):
    delete_expense(expense_id)
    return RedirectResponse(url="/", status_code=303)


@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request, month: str | None = None):
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
    return templates.TemplateResponse(request, "world.html", {})


@app.get("/manifest.json")
async def manifest():
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


@app.get("/health")
async def health():
    return {"status": "ok", "app": "kohvilogi", "version": "0.2.0"}


@app.get("/api/stats")
async def api_stats():
    """Quick stats for the dashboard: streak, totals, progress."""
    from app.database import get_db
    from datetime import date, timedelta

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

    # Total drinks
    total = conn.execute("SELECT COUNT(*) as cnt FROM expenses").fetchone()["cnt"]

    # Unique countries
    countries = conn.execute(
        "SELECT COUNT(DISTINCT country) as cnt FROM expenses WHERE country != ''"
    ).fetchone()["cnt"]

    # Days since first drink
    first = conn.execute("SELECT MIN(date) as d FROM expenses").fetchone()["d"]
    days_since = None
    if first:
        days_since = (date.today() - date.fromisoformat(first)).days + 1

    # This week
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


@app.get("/sw.js", response_class=HTMLResponse)
async def service_worker():
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
});
"""
    return HTMLResponse(content=js, media_type="application/javascript")


# Coffee growing regions (approximate centroids for major regions)
COFFEE_REGIONS = [
    # Africa
    {"name": "Yirgacheffe", "country": "ET", "lat": 6.16, "lon": 38.2, "type": "Arabica", "desc": "Etioopia — kohvi häll"},
    {"name": "Sidamo", "country": "ET", "lat": 5.9, "lon": 38.4, "type": "Arabica", "desc": "Etioopia — puuviljamaitsega"},
    {"name": "Nyeri", "country": "KE", "lat": -0.42, "lon": 36.95, "type": "Arabica", "desc": "Keenia — happeline, intensiivne"},
    {"name": "Kilimanjaro", "country": "TZ", "lat": -3.07, "lon": 37.35, "type": "Arabica", "desc": "Tansaania — mägede kohv"},
    {"name": "Bugisu", "country": "UG", "lat": 1.08, "lon": 34.17, "type": "Arabica/Robusta", "desc": "Uganda — Ida-Aafrika"},
    {"name": "Kivu", "country": "CD", "lat": -2.5, "lon": 28.8, "type": "Arabica", "desc": "Kongo DV — järvede piirkond"},
    # Central America
    {"name": "Antigua", "country": "GT", "lat": 14.56, "lon": -90.73, "type": "Arabica", "desc": "Guatemala — vulkaaniline muld"},
    {"name": "Tarrazú", "country": "CR", "lat": 9.66, "lon": -84.02, "type": "Arabica", "desc": "Costa Rica — kvaliteetne"},
    {"name": "Boquete", "country": "PA", "lat": 8.78, "lon": -82.43, "type": "Arabica", "desc": "Panama — Geisha kohv"},
    {"name": "Jinotega", "country": "NI", "lat": 13.09, "lon": -86.0, "type": "Arabica", "desc": "Nicaragua — mägede kohv"},
    {"name": "Copán", "country": "HN", "lat": 14.83, "lon": -88.75, "type": "Arabica", "desc": "Honduras — soe, puuvilja"},
    {"name": "Apaneca", "country": "SV", "lat": 13.9, "lon": -89.85, "type": "Arabica", "desc": "El Salvador — Bourbon"},
    # South America
    {"name": "Huila", "country": "CO", "lat": 2.5, "lon": -75.5, "type": "Arabica", "desc": "Colombia — maailma kolmas tootja"},
    {"name": "Nariño", "country": "CO", "lat": 1.29, "lon": -77.36, "type": "Arabica", "desc": "Colombia — kõrgmäestik"},
    {"name": "Minas Gerais", "country": "BR", "lat": -18.5, "lon": -44.5, "type": "Arabica/Robusta", "desc": "Brasiilia — maailma suurim tootja"},
    {"name": "Cajamarca", "country": "PE", "lat": -7.16, "lon": -78.5, "type": "Arabica", "desc": "Peruu — orgaaniline"},
    {"name": "Loja", "country": "EC", "lat": -3.99, "lon": -79.2, "type": "Arabica", "desc": "Ecuador — mäestik"},
    # Asia
    {"name": "Aceh / Gayo", "country": "ID", "lat": 4.6, "lon": 96.8, "type": "Arabica/Robusta", "desc": "Indoneesia — Sumatra"},
    {"name": "Java", "country": "ID", "lat": -7.5, "lon": 110.0, "type": "Arabica/Robusta", "desc": "Indoneesia — klassikaline"},
    {"name": "Sulawesi", "country": "ID", "lat": -2.5, "lon": 121.0, "type": "Arabica", "desc": "Indoneesia — keeruline maitse"},
    {"name": "Karnataka", "country": "IN", "lat": 12.5, "lon": 76.0, "type": "Arabica/Robusta", "desc": "India — monsooned Malabar"},
    {"name": "Yunnan", "country": "CN", "lat": 23.5, "lon": 102.0, "type": "Arabica", "desc": "Hiina — kasvav piirkond"},
    {"name": "Đắk Lắk", "country": "VN", "lat": 12.7, "lon": 108.2, "type": "Robusta", "desc": "Vietnam — maailma teine tootja"},
    {"name": "Chikmagalur", "country": "IN", "lat": 13.3, "lon": 75.77, "type": "Arabica", "desc": "India — esimene kohviplantatsioon"},
    {"name": "Shan State", "country": "MM", "lat": 21.0, "lon": 97.0, "type": "Arabica", "desc": "Myanmar — kasvav piirkond"},
    {"name": "Chumphon", "country": "TH", "lat": 10.5, "lon": 99.18, "type": "Arabica/Robusta", "desc": "Tai — Robusta peamiselt"},
    # Caribbean
    {"name": "Blue Mountain", "country": "JM", "lat": 18.08, "lon": -76.6, "type": "Arabica", "desc": "Jamaica — kallis, eksklusiivne"},
    {"name": "Yauco", "country": "PR", "lat": 18.03, "lon": -66.85, "type": "Arabica", "desc": "Puerto Rico — premium"},
]


@app.get("/api/world")
async def api_world():
    """JSON API for coffee map data."""
    data = get_world_stats()
    # Enrich country data
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


@app.get("/api/world/top3")
async def api_world_top3():
    """Top 3 coffee types per country."""
    from app.database import get_db
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

    # Enrich with flags/names
    for cc in result:
        info = COUNTRY_INFO.get(cc, {})
        result[cc] = {
            "coffees": result[cc],
            "flag": info.get("flag", "🏳️"),
            "country_name": info.get("name", cc),
        }

    return result


@app.get("/api/world/by-year")
async def api_world_by_year():
    """Coffee counts by year and country."""
    from app.database import get_db
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


@app.get("/api/share")
async def api_share():
    """Shareable summary for QR code / link."""
    stats = await api_stats()
    import json
    from base64 import b64encode
    payload = b64encode(json.dumps(stats).encode()).decode()
    return {
        **stats,
        "share_url": f"/share/{payload}",
        "text": f"☕ Kohvilogi: {stats['total_drinks']} kohvi, {stats['unique_countries']} riiki, {stats['streak']} päeva streak!",
    }
