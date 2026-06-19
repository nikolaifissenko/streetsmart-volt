#!/usr/bin/env python3
"""Convert Point geometries to LineString by querying Overpass with cleaned names."""
import json
import time
import urllib.request
import urllib.parse
import re
import sys

GEOJSON = "streetsmart_roma.geojson"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "StreetSmart-Build/3.0 (nikolaifissenko@github)"

NAME_CLEAN = {
    "Via Martin Alonzo Pinzon": "Via Martín Alonso Pinzón",
    "Via Leone XIII": "Via Leone XIII",
    "Via del Casale di San Pio V": "Via del Casale di San Pio V",
    "Piazza Vittorio Emanuele Secondo": "Piazza Vittorio Emanuele II",
    "Via dell Esquilino": "Via dell'Esquilino",
    "Via Silvio D Amico": "Via Silvio D'Amico",
    "Viale dell Oceano Atlantico": "Viale dell'Oceano Atlantico",
    "Via Val D Ala": "Via Val d'Ala",
    "Piazza Conca d Oro": "Piazza Conca d'Oro",
    "Via Nomentana (tratto urbano)": "Via Nomentana",
    "Via Nomentana (tratto Mun II)": "Via Nomentana",
    "Via Nomentana (tratto con ciclabile)": "Via Nomentana",
    "Via Nomentana (tratto senza ciclabile)": "Via Nomentana",
    "Via Nomentana (ciclabile confermata)": "Via Nomentana",
    "Via Nomentana (tratto Trieste)": "Via Nomentana",
    "Via Tritone": "Via del Tritone",
    "Via Madonna dei Monti": "Via della Madonna dei Monti",
    "Via Nomentana Nuova": "Via Nomentana Nuova",
    "Viale Trastevere": "Viale di Trastevere",
    "Via XX Settembre": "Via Venti Settembre",
    "Corso d Italia (Porta Pia - P.za Fiume)": "Corso d'Italia",
    "Via Cristoforo Colombo (lato centro ciclabile)": "Via Cristoforo Colombo",
    "Via Cristoforo Colombo (lato EUR)": "Via Cristoforo Colombo",
    "Via Cristoforo Colombo (EUR autostrada urbana)": "Via Cristoforo Colombo",
    "Via Cristoforo Colombo (EUR marciapiede)": "Via Cristoforo Colombo",
    "Via Ostiense (tratto Porto Fluviale-Piazzale Ostiense)": "Via Ostiense",
    "Viale Marconi": "Viale Guglielmo Marconi",
    "Piazza Melozzo da Forli": "Piazza Melozzo da Forlì",
    "Piazzale del Verano (ingresso cimitero)": "Piazzale del Verano",
    "Piazzale del Verano (svincolo)": "Piazzale del Verano",
    "Via del Mare": "Via del Mare",
    "Piazza di Sant'Eustachio": "Piazza Sant'Eustachio",
}


def overpass_query(street_name, lat=None, lon=None):
    clean = street_name.replace("'", "\\'").replace('"', '\\"')
    if lat and lon:
        around = f"(around:500,{lat},{lon})"
        query = f"""[out:json][timeout:60];
(way["name"~"^{clean}$",i]{around};);
out geom;"""
    else:
        query = f"""[out:json][timeout:60];
area["name"="Roma"]["admin_level"="8"]->.roma;
(way["name"~"^{clean}$",i](area.roma););
out geom;"""

    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(OVERPASS_URL, data=data,
                                headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=65) as resp:
                result = json.loads(resp.read())
                elements = result.get("elements", [])
                if not elements:
                    return None
                if len(elements) == 1:
                    el = elements[0]
                    if "geometry" in el:
                        coords = [[p["lon"], p["lat"]] for p in el["geometry"]]
                        return {"type": "LineString", "coordinates": coords}
                else:
                    # Multiple ways - if we have a reference point, pick closest
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
                            if best is None:
                                best = coords
                            else:
                                best = best + coords
                    if best:
                        return {"type": "LineString", "coordinates": best}
                return None
        except Exception as e:
            print(f"    attempt {attempt+1} error: {e}")
            time.sleep(5 * (attempt + 1))
    return None


with open(GEOJSON) as f:
    gj = json.load(f)

points = [(i, f) for i, f in enumerate(gj["features"])
          if f["geometry"] and f["geometry"]["type"] == "Point"]

print(f"Points to convert: {len(points)}")
converted = 0
failed_names = []

for idx, (i, feat) in enumerate(points):
    nome = feat["properties"]["nome"]
    search = NAME_CLEAN.get(nome, nome)
    # Remove parenthetical notes
    search_clean = re.sub(r'\s*\([^)]*\)', '', search).strip()

    lon, lat = feat["geometry"]["coordinates"]

    print(f"[{idx+1}/{len(points)}] {nome} -> {search_clean}")

    geom = overpass_query(search_clean, lat, lon)
    if geom:
        gj["features"][i]["geometry"] = geom
        converted += 1
        print(f"  OK ({len(geom['coordinates'])} points)")
    else:
        failed_names.append(nome)
        print(f"  FAILED - keeping as Point")

    time.sleep(3)

with open(GEOJSON, "w") as f:
    json.dump(gj, f, ensure_ascii=False)
with open("dist/streetsmart_roma.geojson", "w") as f:
    json.dump(gj, f, ensure_ascii=False)

print(f"\nConverted: {converted}/{len(points)}")
print(f"Still points: {len(failed_names)}")
if failed_names:
    print("Failed:")
    for n in failed_names:
        print(f"  - {n}")
