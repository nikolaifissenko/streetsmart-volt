#!/usr/bin/env python3
"""
StreetSmart build.py v3
Legge data/master/streetsmart_roma_completo.csv
→ valida ogni riga
→ fetcha geometrie reali (LineString) da Overpass in batch da N strade
→ fallback Point da Nominatim per strade non trovate
→ produce dist/streetsmart_roma.geojson + streetsmart_roma.geojson (root)
"""

import csv
import json
import time
import sys
import re
import urllib.request
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).parent.parent
MASTER_CSV = ROOT / "data" / "master" / "streetsmart_roma_completo.csv"
DIST_DIR   = ROOT / "dist"
OUTPUT_GJ  = DIST_DIR / "streetsmart_roma.geojson"
ROOT_GJ    = ROOT / "streetsmart_roma.geojson"
CACHE_FILE = ROOT / "data" / "master" / ".geocode_cache.json"

VALID_CLASSIFICATIONS = {"nero","rosso","giallo","verde","blu","verde-giallo","verde-blu"}
SCORE_MAP = {"nero":5,"rosso":4,"giallo":3,"blu":2,"verde-giallo":2,"verde-blu":1,"verde":1}
REQUIRED_FIELDS = ["id","nome","quartiere","classificazione","score","municipio"]

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "StreetSmart-Build/3.0 (nikolaifissenko@github)"
BATCH_SIZE = 20          # strade per query Overpass
BATCH_DELAY = 5.0        # secondi tra batch Overpass
NOM_DELAY = 1.5          # secondi tra chiamate Nominatim
OVERPASS_TIMEOUT = 45    # secondi timeout query


def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def clean_name(nome):
    return re.sub(r'\s*\(.*?\)', '', nome).strip()


ROME_BBOX = "41.6,12.2,42.1,12.8"  # bounding box Roma

def overpass_batch(names):
    """
    Fetcha le geometrie di più strade in una singola query Overpass.
    Ritorna dict {name: geometry} per le strade trovate.
    """
    escaped = [re.escape(n) for n in names]
    regex = "^(" + "|".join(escaped) + ")$"

    query = f"""
[out:json][timeout:{OVERPASS_TIMEOUT}];
(
  way["name"~"{regex}"]["highway"]({ROME_BBOX});
);
out geom;
"""
    data = query.encode("utf-8")
    req = urllib.request.Request(
        OVERPASS_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": USER_AGENT},
    )

    try:
        with urllib.request.urlopen(req, timeout=OVERPASS_TIMEOUT + 10) as resp:
            result = json.loads(resp.read().decode())
    except Exception as e:
        print(f"\n  [WARN] Overpass batch fallito: {e}")
        return {}

    # Raggruppa way per nome → MultiLineString o LineString
    by_name = {}
    for el in result.get("elements", []):
        name = el.get("tags", {}).get("name", "")
        if not name:
            continue
        geom_pts = el.get("geometry", [])
        if len(geom_pts) < 2:
            continue
        coords = [[pt["lon"], pt["lat"]] for pt in geom_pts]
        by_name.setdefault(name, []).append(coords)

    out = {}
    for name, lines in by_name.items():
        if len(lines) == 1:
            out[name] = {"type": "LineString", "coordinates": lines[0]}
        else:
            out[name] = {"type": "MultiLineString", "coordinates": lines}
    return out


def nominatim_point(nome_clean, quartiere):
    query = f"{nome_clean}, {quartiere}, Roma, Italia"
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1,
                                     "countrycodes": "it", "addressdetails": 0})
    req = urllib.request.Request(
        f"{NOMINATIM_URL}?{params}",
        headers={"User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        time.sleep(NOM_DELAY)
        if data:
            return {"type": "Point", "coordinates": [float(data[0]["lon"]), float(data[0]["lat"])]}
        return None
    except Exception as e:
        print(f"\n  [WARN] Nominatim fallito per '{nome_clean}': {e}")
        return None


def validate_row(row):
    errors = []
    for field in REQUIRED_FIELDS:
        if not row.get(field, "").strip():
            errors.append(f"campo '{field}' mancante")
    id_val = row.get("id", "")
    if id_val and not id_val.startswith("SS-ROM-"):
        errors.append(f"ID non valido: '{id_val}'")
    cls = row.get("classificazione", "").strip()
    if cls and cls not in VALID_CLASSIFICATIONS:
        errors.append(f"classificazione sconosciuta: '{cls}'")
    if cls in SCORE_MAP:
        exp = str(SCORE_MAP[cls])
        act = row.get("score", "").strip()
        if act and act != exp:
            errors.append(f"score {act} != atteso {exp} per {cls}")
    return errors


def main():
    print("=" * 60)
    print("StreetSmart build.py v3 — batch Overpass + Nominatim")
    print("=" * 60)

    if not MASTER_CSV.exists():
        print(f"ERRORE: {MASTER_CSV} non trovato")
        sys.exit(1)

    DIST_DIR.mkdir(exist_ok=True)
    cache = load_cache()

    rows = []
    errors_total = []
    with open(MASTER_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            row = {k: v.strip() for k, v in row.items()}
            for e in validate_row(row):
                errors_total.append(f"  Riga {i} ({row.get('id','')}): {e}")
            rows.append(row)

    print(f"Righe lette:  {len(rows)}")
    print(f"Errori CSV:   {len(errors_total)}")
    for e in errors_total:
        print(e)

    # Strade che mancano dalla cache (chiave "v3|nome_clean")
    missing = []
    for row in rows:
        nc = clean_name(row["nome"])
        if f"v3|{nc}" not in cache:
            missing.append(row)

    print(f"\nCache: {len(rows)-len(missing)} strade già presenti")
    print(f"Da fetchare: {len(missing)} strade")

    if missing:
        # ── FASE 1: Overpass in batch ─────────────────────────────
        print("\nFase 1 — Overpass batch query…")
        batches = [missing[i:i+BATCH_SIZE] for i in range(0, len(missing), BATCH_SIZE)]
        overpass_hits = 0
        not_found = []

        for bi, batch in enumerate(batches):
            names = [clean_name(r["nome"]) for r in batch]
            print(f"  Batch {bi+1}/{len(batches)}: {len(names)} strade… ", end="", flush=True)
            results = overpass_batch(names)
            print(f"{len(results)} trovate")

            for row in batch:
                nc = clean_name(row["nome"])
                # Prova match esatto o case-insensitive
                geom = results.get(nc)
                if geom is None:
                    for k, v in results.items():
                        if k.lower() == nc.lower():
                            geom = v
                            break
                if geom:
                    cache[f"v3|{nc}"] = geom
                    overpass_hits += 1
                else:
                    not_found.append(row)

            if bi < len(batches) - 1:
                time.sleep(BATCH_DELAY)

        save_cache(cache)
        print(f"  → {overpass_hits} linee da Overpass, {len(not_found)} non trovate")

        # ── FASE 2: Nominatim fallback per le strade mancanti ─────
        if not_found:
            print(f"\nFase 2 — Nominatim fallback per {len(not_found)} strade…")
            nom_ok, nom_fail = 0, 0
            for row in not_found:
                nc = clean_name(row["nome"])
                geom = nominatim_point(nc, row.get("quartiere", ""))
                cache[f"v3|{nc}"] = geom
                if geom:
                    nom_ok += 1
                else:
                    nom_fail += 1
                sys.stdout.write(f"\r  ok:{nom_ok}  falliti:{nom_fail}    ")
                sys.stdout.flush()
            print()
            save_cache(cache)
            print(f"  → {nom_ok} punti da Nominatim, {nom_fail} senza geometria")

    # ── Produzione GeoJSON ────────────────────────────────────────
    features = []
    stats = {"linee": 0, "punti": 0, "nessuna": 0}
    for row in rows:
        nc = clean_name(row["nome"])
        geom = cache.get(f"v3|{nc}")

        if geom is None:
            stats["nessuna"] += 1
        elif geom.get("type") == "Point":
            stats["punti"] += 1
        else:
            stats["linee"] += 1

        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "id":              row.get("id",""),
                "nome":            row.get("nome",""),
                "quartiere":       row.get("quartiere",""),
                "municipio":       row.get("municipio",""),
                "classificazione": row.get("classificazione",""),
                "score":           int(row["score"]) if row.get("score") else None,
                "ciclabile":       row.get("ciclabile_presente",""),
                "n_corsie":        int(row["n_corsie"]) if row.get("n_corsie") else None,
                "senso_unico":     row.get("senso_unico",""),
                "n_testimonianze": int(row["n_testimonianze"]) if row.get("n_testimonianze") else None,
                "note":            row.get("note",""),
            }
        })

    gj = {"type": "FeatureCollection", "features": features}
    for path in [OUTPUT_GJ, ROOT_GJ]:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(gj, f, ensure_ascii=False, indent=2)

    print(f"\nGeoJSON scritto in:")
    print(f"  {OUTPUT_GJ}")
    print(f"  {ROOT_GJ}")
    print(f"\n  LineString/Multi: {stats['linee']}")
    print(f"  Point (fallback): {stats['punti']}")
    print(f"  Senza geometria:  {stats['nessuna']}")

    by_class = {}
    for row in rows:
        c = row.get("classificazione","?")
        by_class[c] = by_class.get(c,0) + 1
    print(f"\nDistribuzione:")
    for cls, count in sorted(by_class.items(), key=lambda x: -x[1]):
        print(f"  {cls:<14} {count:>3}")
    print("=" * 60)


if __name__ == "__main__":
    main()
