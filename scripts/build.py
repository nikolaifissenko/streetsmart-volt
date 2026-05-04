#!/usr/bin/env python3
"""
StreetSmart build.py
Legge data/master/streetsmart_roma_completo.csv
→ valida ogni riga
→ geocodifica via Nominatim (OSM) le strade senza coordinate
→ produce dist/streetsmart_roma.geojson

Uso: python scripts/build.py
"""

import csv
import json
import time
import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
MASTER_CSV = ROOT / "data" / "master" / "streetsmart_roma_completo.csv"
DIST_DIR = ROOT / "dist"
OUTPUT_GEOJSON = DIST_DIR / "streetsmart_roma.geojson"
CACHE_FILE = ROOT / "data" / "master" / ".geocode_cache.json"

VALID_CLASSIFICATIONS = {"nero", "rosso", "giallo", "verde", "blu", "verde-giallo", "verde-blu"}
SCORE_MAP = {"nero": 5, "rosso": 4, "giallo": 3, "blu": 2, "verde-giallo": 2, "verde-blu": 1, "verde": 1}
REQUIRED_FIELDS = ["id", "nome", "quartiere", "classificazione", "score", "municipio"]

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_DELAY = 1.1  # secondi tra richieste (rispetta usage policy)
USER_AGENT = "StreetSmart-Build/1.0 (nikolaifissenko@github)"

# ── GEOCODING CACHE ──────────────────────────────────────────────────────────

def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def geocode(nome, quartiere, cache):
    key = f"{nome}|{quartiere}"
    if key in cache:
        return cache[key]

    query = f"{nome}, {quartiere}, Roma, Italia"
    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "it",
        "addressdetails": 0,
    })
    url = f"{NOMINATIM_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        time.sleep(NOMINATIM_DELAY)
        if data:
            result = {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
        else:
            result = None
    except Exception as e:
        print(f"    [WARN] Geocoding fallito per '{nome}': {e}")
        result = None

    cache[key] = result
    return result

# ── VALIDAZIONE ──────────────────────────────────────────────────────────────

def validate_row(row, line_num):
    errors = []

    # Campi obbligatori
    for field in REQUIRED_FIELDS:
        if not row.get(field, "").strip():
            errors.append(f"campo '{field}' mancante")

    # Formato ID
    id_val = row.get("id", "")
    if id_val and not id_val.startswith("SS-ROM-"):
        errors.append(f"ID formato non valido: '{id_val}'")

    # Classificazione valida
    cls = row.get("classificazione", "").strip()
    if cls and cls not in VALID_CLASSIFICATIONS:
        errors.append(f"classificazione sconosciuta: '{cls}'")

    # Score coerente con classificazione
    if cls in SCORE_MAP:
        expected_score = str(SCORE_MAP[cls])
        actual_score = row.get("score", "").strip()
        if actual_score and actual_score != expected_score:
            errors.append(f"score {actual_score} non corrisponde a {cls} (atteso {expected_score})")

    return errors

# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("StreetSmart build.py")
    print("=" * 60)

    if not MASTER_CSV.exists():
        print(f"ERRORE: file non trovato: {MASTER_CSV}")
        sys.exit(1)

    DIST_DIR.mkdir(exist_ok=True)
    cache = load_cache()

    rows = []
    errors_total = []

    with open(MASTER_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            row = {k: v.strip() for k, v in row.items()}
            errs = validate_row(row, i)
            if errs:
                for e in errs:
                    errors_total.append(f"  Riga {i} ({row.get('id','')}): {e}")
            rows.append(row)

    print(f"\nRighe lette:    {len(rows)}")
    print(f"Errori trovati: {len(errors_total)}")
    if errors_total:
        print("\nERRORI DI VALIDAZIONE:")
        for e in errors_total:
            print(e)
        print()

    # Geocoding
    without_coords = [r for r in rows if not r.get("lat") or not r.get("lon")]
    print(f"Strade senza coordinate: {len(without_coords)}")

    if without_coords:
        print(f"Geocodifica in corso (max {len(without_coords)} richieste OSM)…")
        geocoded = 0
        failed = 0
        for row in without_coords:
            result = geocode(row["nome"], row["quartiere"], cache)
            if result:
                row["lat"] = result["lat"]
                row["lon"] = result["lon"]
                geocoded += 1
            else:
                failed += 1
            sys.stdout.write(f"\r  {geocoded} ok, {failed} falliti     ")
            sys.stdout.flush()
        print()
        save_cache(cache)
        print(f"Cache salvata: {CACHE_FILE}")

    # Produzione GeoJSON
    features = []
    no_coords = 0
    for row in rows:
        lat = row.get("lat")
        lon = row.get("lon")

        if not lat or not lon:
            no_coords += 1
            geometry = None
        else:
            geometry = {
                "type": "Point",
                "coordinates": [float(lon), float(lat)]
            }

        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id":               row.get("id", ""),
                "nome":             row.get("nome", ""),
                "quartiere":        row.get("quartiere", ""),
                "municipio":        row.get("municipio", ""),
                "classificazione":  row.get("classificazione", ""),
                "score":            int(row["score"]) if row.get("score") else None,
                "ciclabile":        row.get("ciclabile_presente", ""),
                "n_corsie":         int(row["n_corsie"]) if row.get("n_corsie") else None,
                "senso_unico":      row.get("senso_unico", ""),
                "n_testimonianze":  int(row["n_testimonianze"]) if row.get("n_testimonianze") else None,
                "note":             row.get("note", ""),
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(OUTPUT_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    # Report finale
    by_class = {}
    for row in rows:
        c = row.get("classificazione", "sconosciuta")
        by_class[c] = by_class.get(c, 0) + 1

    print(f"\nGeoJSON prodotto: {OUTPUT_GEOJSON}")
    print(f"  Feature totali:      {len(features)}")
    print(f"  Con coordinate:      {len(features) - no_coords}")
    print(f"  Senza coordinate:    {no_coords}")
    print(f"\nDistribuzione classificazioni:")
    for cls, count in sorted(by_class.items(), key=lambda x: -x[1]):
        bar = "█" * (count // 2)
        print(f"  {cls:<14} {count:>3}  {bar}")

    if errors_total:
        print(f"\n[ATTENZIONE] {len(errors_total)} errori di validazione — controlla il CSV.")
    else:
        print("\nValidazione OK — nessun errore.")

    print("=" * 60)

if __name__ == "__main__":
    main()
