#!/usr/bin/env python3
"""Fix missing geometries by retrying with cleaned street names via Nominatim."""
import json
import time
import urllib.request
import urllib.parse

GEOJSON = "streetsmart_roma.geojson"
CACHE_FILE = "data/master/.geocode_cache.json"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "StreetSmart-Build/3.0 (nikolaifissenko@github)"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def nom_search(street_name):
    params = urllib.parse.urlencode({
        "q": street_name + ", Roma, Italia",
        "format": "json",
        "limit": "1",
        "addressdetails": "1",
    })
    req = urllib.request.Request(
        f"{NOMINATIM_URL}?{params}",
        headers={"User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if data:
                return [float(data[0]["lon"]), float(data[0]["lat"])]
    except Exception as e:
        print(f"  Nominatim error: {e}")
    return None

def overpass_search(street_name):
    clean = street_name.replace("'", "\\'")
    query = f"""[out:json][timeout:30];
area["name"="Roma"]["admin_level"="8"]->.roma;
(way["name"~"{clean}",i](area.roma););
out geom;"""
    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(OVERPASS_URL, data=data, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            result = json.loads(resp.read())
            if result.get("elements"):
                el = result["elements"][0]
                if "geometry" in el:
                    coords = [[p["lon"], p["lat"]] for p in el["geometry"]]
                    return {"type": "LineString", "coordinates": coords}
    except Exception as e:
        print(f"  Overpass error: {e}")
    return None

NAME_FIXES = {
    "Via Biberatica": "Via Biberatica",
    "Via Baccina": "Via Baccina",
    "Corso del Rinascimento": "Corso del Rinascimento",
    "Via Giustiniani": "Via Giustiniani",
    "Piazza di Sant'Eustachio": "Piazza di Sant Eustachio",
    "Via di Tor Millina": "Via di Tor Millina",
    "Via della Corda": "Via della Corda",
    "Via degli Ausoni": "Via degli Ausoni",
    "Via dei Ramni": "Via dei Ramni",
    "Via dei Taurini": "Via dei Taurini",
    "Via dei Marrucini": "Via dei Marrucini",
    "Via Pavia": "Via Pavia",
    "Piazza Vittorio Emanuele Secondo": "Piazza Vittorio Emanuele II",
    "Via Rodolfo Lanciani": "Via Rodolfo Lanciani",
    "Via Giovanni Giolitti": "Via Giovanni Giolitti",
    "Piazza Lodi": "Piazza Lodi",
    "Via La Spezia": "Via La Spezia",
    "Via Terni": "Via Terni",
    "Via Voghera": "Via Voghera",
    "Via dell Esquilino": "Via dell'Esquilino",
    "Via Val D Ala": "Via Val d'Ala",
    "Piazza Conca d Oro": "Piazza Conca d'Oro",
    "Via dell Oceano Indiano": "Via dell'Oceano Indiano",
    "Via San Francesco a Ripa": "Via di San Francesco a Ripa",
    "Via Santa Maria in Trastevere": "Via di Santa Maria in Trastevere",
    "Via Lario": "Via Lario",
    "Viale Marconi": "Viale Guglielmo Marconi",
}

with open(GEOJSON) as f:
    gj = json.load(f)

with open(CACHE_FILE) as f:
    cache = json.load(f)

fixed = 0
for feature in gj["features"]:
    if feature["geometry"] is not None:
        continue
    nome = feature["properties"]["nome"]
    search_name = NAME_FIXES.get(nome, nome)

    print(f"Trying: {nome} -> {search_name}")

    # Try Overpass first for LineString
    geom = overpass_search(search_name)
    if geom:
        feature["geometry"] = geom
        cache[nome] = geom
        fixed += 1
        print(f"  FIXED via Overpass (LineString)")
        time.sleep(2)
        continue

    time.sleep(2)

    # Fallback to Nominatim for Point
    coords = nom_search(search_name)
    if coords:
        feature["geometry"] = {"type": "Point", "coordinates": coords}
        cache[nome] = {"type": "Point", "coordinates": coords}
        fixed += 1
        print(f"  FIXED via Nominatim (Point)")
    else:
        print(f"  STILL MISSING")
    time.sleep(2)

with open(GEOJSON, "w") as f:
    json.dump(gj, f, ensure_ascii=False)
with open("dist/streetsmart_roma.geojson", "w") as f:
    json.dump(gj, f, ensure_ascii=False)
with open(CACHE_FILE, "w") as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"\nFixed {fixed} streets")
remaining = sum(1 for f in gj["features"] if f["geometry"] is None)
print(f"Still missing: {remaining}")
