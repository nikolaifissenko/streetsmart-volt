#!/usr/bin/env python3
"""
build_fast.py — Genera GeoJSON da CSV + Overpass in un'unica query bulk.
Molto più veloce di build.py per grandi volumi.
"""

import csv
import json
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent
MASTER_CSV = ROOT / "data" / "master" / "streetsmart_roma_completo.csv"
DIST_DIR   = ROOT / "dist"
OUTPUT_GJ  = DIST_DIR / "streetsmart_roma.geojson"
ROOT_GJ    = ROOT / "streetsmart_roma.geojson"
CACHE_FILE = ROOT / "data" / "master" / ".geocode_cache.json"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "StreetSmart-Build/4.0 (nikolaifissenko@github)"

VALID_CLASSIFICATIONS = {"nero","rosso","giallo","verde","blu","verde-giallo","verde-blu"}
SCORE_MAP = {"nero":5,"rosso":4,"giallo":3,"blu":2,"verde-giallo":2,"verde-blu":1,"verde":1}


def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)


def clean_name(nome):
    return re.sub(r'\s*\(.*?\)', '', nome).strip()


def load_csv():
    rows = []
    with open(MASTER_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("classificazione") not in VALID_CLASSIFICATIONS:
                continue
            rows.append(row)
    return rows


def overpass_batch(names, batch_num, total_batches):
    """Fetch geometries for a batch of street names."""
    escaped = [re.escape(n) for n in names]
    regex = "^(" + "|".join(escaped) + ")$"

    query = f"""
[out:json][timeout:90];
(
  way["name"~"{regex}",i](41.65,12.23,42.02,12.73);
);
out geom;
"""
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(
        OVERPASS_URL,
        data=data,
        headers={"User-Agent": USER_AGENT},
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result.get("elements", [])
    except Exception as e:
        print(f"  Batch {batch_num}/{total_batches} error: {e}")
        return []


def elements_to_geom(elements, name):
    """Convert Overpass elements to a GeoJSON geometry for a given street name."""
    matching = [el for el in elements
                if el.get("tags", {}).get("name", "").lower() == name.lower()
                and el.get("geometry")]

    if not matching:
        return None

    lines = []
    for el in matching:
        coords = [[pt["lon"], pt["lat"]] for pt in el["geometry"]]
        if len(coords) >= 2:
            lines.append(coords)

    if not lines:
        return None
    if len(lines) == 1:
        return {"type": "LineString", "coordinates": lines[0]}
    return {"type": "MultiLineString", "coordinates": lines}


def main():
    print("=" * 60)
    print("StreetSmart — Build GeoJSON (fast bulk mode)")
    print("=" * 60)

    rows = load_csv()
    print(f"Strade nel CSV: {len(rows)}")

    cache = load_cache()
    print(f"Geometrie in cache: {len(cache)}")

    # Find streets that need geometry
    need_geom = []
    cached_count = 0
    for row in rows:
        name = clean_name(row["nome"])
        cache_key = name.lower()
        if cache_key in cache and cache[cache_key] and cache[cache_key].get("type") in ("LineString", "MultiLineString"):
            cached_count += 1
        else:
            need_geom.append(name)

    # Deduplicate names to fetch
    unique_names = list(set(need_geom))
    print(f"Geometrie già in cache: {cached_count}")
    print(f"Strade da cercare: {len(unique_names)}")

    # Fetch in batches
    BATCH_SIZE = 40
    batches = [unique_names[i:i+BATCH_SIZE] for i in range(0, len(unique_names), BATCH_SIZE)]
    total_batches = len(batches)

    if batches:
        print(f"\nFetching geometrie in {total_batches} batch da {BATCH_SIZE}...")

    all_elements = []
    for i, batch in enumerate(batches):
        print(f"  Batch {i+1}/{total_batches} ({len(batch)} strade)...", end=" ", flush=True)
        elements = overpass_batch(batch, i+1, total_batches)
        print(f"→ {len(elements)} ways")
        all_elements.extend(elements)

        # Cache results
        found_names = set()
        for el in elements:
            el_name = el.get("tags", {}).get("name", "")
            if el_name:
                found_names.add(el_name.lower())

        for name in batch:
            geom = elements_to_geom(elements, name)
            cache_key = name.lower()
            if geom:
                cache[cache_key] = geom
            elif cache_key not in cache:
                cache[cache_key] = None

        if i < total_batches - 1:
            time.sleep(6)

    save_cache(cache)
    print(f"\nCache aggiornata: {len(cache)} entries")

    # Build GeoJSON
    features = []
    with_geom = 0
    without_geom = 0

    for row in rows:
        name = clean_name(row["nome"])
        cache_key = name.lower()
        geom = cache.get(cache_key)

        # Only include LineString/MultiLineString
        if geom and geom.get("type") in ("LineString", "MultiLineString"):
            with_geom += 1
        else:
            without_geom += 1
            continue

        properties = {
            "id": row["id"],
            "nome": row["nome"],
            "quartiere": row.get("quartiere", ""),
            "classificazione": row["classificazione"],
            "score": int(row.get("score", SCORE_MAP.get(row["classificazione"], 3))),
            "note": row.get("note", ""),
            "ciclabile": row.get("ciclabile_presente", ""),
            "n_corsie": row.get("n_corsie", ""),
            "senso_unico": row.get("senso_unico", ""),
            "n_testimonianze": row.get("n_testimonianze", ""),
            "municipio": row.get("municipio", ""),
        }

        features.append({
            "type": "Feature",
            "properties": properties,
            "geometry": geom,
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    DIST_DIR.mkdir(exist_ok=True)
    for path in (OUTPUT_GJ, ROOT_GJ):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"GeoJSON generato: {len(features)} strade con geometria")
    print(f"  Con geometria: {with_geom}")
    print(f"  Senza geometria (escluse): {without_geom}")
    print(f"  File: {ROOT_GJ}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
