#!/usr/bin/env python3
"""Second pass to fix remaining Point geometries with better name matching."""
import json
import time
import urllib.request
import urllib.parse

GEOJSON = "streetsmart_roma.geojson"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "StreetSmart-Build/3.0 (nikolaifissenko@github)"

FIXES = {
    "Lungotevere Sanzio": "Lungotevere Raffaello Sanzio",
    "Via San Francesco a Ripa": "Via di San Francesco a Ripa",
    "Via Gregorio VII": "Via Gregorio VII",
    "Via Lario": "Via Lario",
    "Via Mercadante": "Via Saverio Mercadante",
    "Via Paisiello": "Via Giovanni Paisiello",
    "Via Spontini": "Via Gaspare Spontini",
    "Via Bellini": "Via Vincenzo Bellini",
    "Via Donizetti": "Via Gaetano Donizetti",
    "Via Reni": "Via Guido Reni",
    "Via Mangili": "Via Giuseppe Mangili",
    "Via Val Melaina": "Via Val Melaina",
    "Via Castel Giubileo": "Via di Castel Giubileo",
    "Via Sacco Pastore": "Via di Sacco Pastore",
    "Viale Artigianato": "Viale dell'Artigianato",
    "Via Grimaldi": "Via Giovanni Francesco Grimaldi",
    "Via Barrili": "Via Anton Giulio Barrili",
    "Via Poerio": "Via Alessandro Poerio",
    "Via di Pietralata": "Via di Pietralata",
    "Via Martin Alonzo Pinzon": "Via Martín Alonso Pinzón",
    "Via Leone XIII": "Via di Leone XIII",
    "Via del Casale di San Pio V": "Via del Casaletto di San Pio V",
    "Via Biberatica": "Via Biberatica",
    "Piazza di Sant'Eustachio": "Piazza di Sant'Eustachio",
}

def overpass_query(street_name, lat=None, lon=None):
    clean = street_name.replace("'", "\\'").replace('"', '\\"')
    if lat and lon:
        query = f"""[out:json][timeout:60];
(way["name"~"{clean}",i](around:800,{lat},{lon}););
out geom;"""
    else:
        query = f"""[out:json][timeout:60];
area["name"="Roma"]["admin_level"="8"]->.roma;
(way["name"~"{clean}",i](area.roma););
out geom;"""
    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(OVERPASS_URL, data=data, headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=65) as resp:
                result = json.loads(resp.read())
                elements = result.get("elements", [])
                if not elements:
                    return None
                best = None
                best_dist = float('inf')
                for el in elements:
                    if "geometry" not in el:
                        continue
                    coords = [[p["lon"], p["lat"]] for p in el["geometry"]]
                    if lat and lon:
                        mid = len(coords) // 2
                        d = (coords[mid][1] - lat)**2 + (coords[mid][0] - lon)**2
                        if d < best_dist:
                            best_dist = d
                            best = coords
                    else:
                        best = coords
                        break
                if best:
                    return {"type": "LineString", "coordinates": best}
                return None
        except Exception as e:
            print(f"    attempt {attempt+1}: {e}")
            time.sleep(8 * (attempt + 1))
    return None

with open(GEOJSON) as f:
    gj = json.load(f)

converted = 0
for feat in gj["features"]:
    if not feat["geometry"] or feat["geometry"]["type"] != "Point":
        continue
    nome = feat["properties"]["nome"]
    if nome not in FIXES:
        continue
    search = FIXES[nome]
    lon, lat = feat["geometry"]["coordinates"]
    print(f"{nome} -> {search}")
    geom = overpass_query(search, lat, lon)
    if geom:
        feat["geometry"] = geom
        converted += 1
        print(f"  OK ({len(geom['coordinates'])} pts)")
    else:
        print(f"  STILL FAILED")
    time.sleep(4)

with open(GEOJSON, "w") as f:
    json.dump(gj, f, ensure_ascii=False)
with open("dist/streetsmart_roma.geojson", "w") as f:
    json.dump(gj, f, ensure_ascii=False)

remaining = sum(1 for f in gj["features"] if f["geometry"] and f["geometry"]["type"] == "Point")
print(f"\nFixed: {converted}")
print(f"Remaining points: {remaining}")
