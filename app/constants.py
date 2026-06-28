"""Kohvilogi konstandid — kohvitüübid, valuutad, riigid, kohviregioonid."""

# Lowercase set for validation
VALID_COFFEE_TYPES = {
    "espresso", "americano", "cappuccino", "latte", "flat white",
    "macchiato", "mocha", "ristretto", "lungo", "cold brew",
    "filterkohv", "muu",
}

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
    "RW": {"name": "Rwanda", "flag": "🇷🇼"}, "ZM": {"name": "Sambia", "flag": "🇿🇲"},
    "ZW": {"name": "Zimbabwe", "flag": "🇿🇼"}, "MW": {"name": "Malawi", "flag": "🇲🇼"},
    "MZ": {"name": "Mosambiik", "flag": "🇲🇿"}, "MG": {"name": "Madagaskar", "flag": "🇲🇬"},
    "MU": {"name": "Mauritius", "flag": "🇲🇺"}, "SC": {"name": "Seišellid", "flag": "🇸🇨"},
    "CV": {"name": "Roheneemesaared", "flag": "🇨🇻"}, "CL": {"name": "Tšiili", "flag": "🇨🇱"},
    "PY": {"name": "Paraguay", "flag": "🇵🇾"}, "UY": {"name": "Uruguay", "flag": "🇺🇾"},
    "BO": {"name": "Boliivia", "flag": "🇧🇴"}, "GY": {"name": "Guyana", "flag": "🇬🇾"},
    "SR": {"name": "Suriname", "flag": "🇸🇷"}, "VE": {"name": "Venezuela", "flag": "🇻🇪"},
    "TT": {"name": "Trinidad", "flag": "🇹🇹"}, "BB": {"name": "Barbados", "flag": "🇧🇧"},
    "BS": {"name": "Bahama", "flag": "🇧🇸"}, "FO": {"name": "Fääri saared", "flag": "🇫🇴"},
    "GL": {"name": "Gröönimaa", "flag": "🇬🇱"}, "SJ": {"name": "Svalbard", "flag": "🇸🇯"},
}

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

# Derived sets for validation (placed after COUNTRY_INFO to capture all entries)
VALID_COUNTRIES = set(COUNTRY_INFO.keys())
