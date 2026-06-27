#!/usr/bin/env python3
"""
import_osm_bulk.py — Importa strade di Roma da OpenStreetMap e le pre-classifica.

Logica di classificazione automatica basata su tag OSM:
- NERO (5): highway=trunk/primary + lanes>=4, o maxspeed>=70
- ROSSO (4): highway=primary/secondary senza ciclabile, o lanes>=3
- GIALLO (3): highway=tertiary/residential/unclassified senza ciclabile
- VERDE (1): cycleway presente (tag cycleway o highway=cycleway)
- BLU (2): highway=pedestrian/living_street, o access=no/private (ZTL)

Evita duplicati con strade già presenti nel CSV master.
Produce un file CSV con le nuove strade da aggiungere.
"""

import json
import csv
import time
import re
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent
MASTER_CSV = ROOT / "data" / "master" / "streetsmart_roma_completo.csv"
OUTPUT_CSV = ROOT / "data" / "master" / "osm_import_new_streets.csv"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "StreetSmart-Import/1.0 (nikolaifissenko@github)"
ROME_BBOX = "41.65,12.23,42.02,12.73"

MUNICIPIO_POLYGONS = None  # Would need shapefiles for exact mapping

# Highway types we care about
RELEVANT_HIGHWAYS = {
    "motorway", "trunk", "primary", "secondary", "tertiary",
    "residential", "unclassified", "living_street", "pedestrian",
    "cycleway", "service",
}

# Skip these
SKIP_HIGHWAYS = {"motorway", "motorway_link", "service"}


def load_existing_names():
    """Load all existing street names from master CSV."""
    names = set()
    with open(MASTER_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["nome"].strip().lower()
            name = re.sub(r'\s*\(.*?\)', '', name).strip()
            names.add(name)
    return names


def get_last_id():
    """Get the last used ID number."""
    last = 0
    with open(MASTER_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = re.match(r'SS-ROM-(\d+)', row["id"])
            if m:
                last = max(last, int(m.group(1)))
    return last


def classify_street(tags):
    """
    Classify a street based on OSM tags.
    Returns (classificazione, score, note, ciclabile, n_corsie).
    """
    highway = tags.get("highway", "")
    lanes_str = tags.get("lanes", "")
    maxspeed_str = tags.get("maxspeed", "")
    cycleway = tags.get("cycleway", "")
    cycleway_left = tags.get("cycleway:left", "")
    cycleway_right = tags.get("cycleway:right", "")
    cycleway_both = tags.get("cycleway:both", "")
    access = tags.get("access", "")
    bicycle = tags.get("bicycle", "")
    oneway = tags.get("oneway", "no")

    lanes = 0
    if lanes_str:
        try:
            lanes = int(lanes_str)
        except ValueError:
            pass

    maxspeed = 0
    if maxspeed_str:
        try:
            maxspeed = int(re.sub(r'[^\d]', '', maxspeed_str))
        except ValueError:
            pass

    has_cycleway = (
        highway == "cycleway" or
        cycleway in ("lane", "track", "shared_lane", "share_busway", "opposite_lane", "opposite_track") or
        cycleway_left in ("lane", "track") or
        cycleway_right in ("lane", "track") or
        cycleway_both in ("lane", "track") or
        bicycle == "designated"
    )

    is_pedestrian = highway in ("pedestrian", "living_street")
    is_ztl = access in ("no", "private", "destination") and highway not in ("motorway", "trunk")

    senso_unico = "si" if oneway in ("yes", "true", "1") else "no"

    # Classification logic
    if has_cycleway:
        note = "ciclabile presente (da OpenStreetMap)"
        return "verde", 1, note, "si", lanes or 2, senso_unico

    if is_pedestrian or is_ztl:
        if is_pedestrian:
            note = f"zona pedonale / living street"
        else:
            note = f"accesso limitato (ZTL)"
        return "blu", 2, note, "no", lanes or 1, senso_unico

    if highway in ("trunk", "trunk_link") or maxspeed >= 70:
        note = f"strada ad alta velocità ({highway}"
        if maxspeed:
            note += f", {maxspeed} km/h"
        if lanes >= 4:
            note += f", {lanes} corsie"
        note += ")"
        return "nero", 5, note, "no", lanes or 4, senso_unico

    if highway in ("primary", "primary_link"):
        if lanes >= 4:
            note = f"strada principale {lanes} corsie senza protezione ciclabile"
            return "nero", 5, note, "no", lanes, senso_unico
        note = f"strada principale trafficata"
        if lanes:
            note += f" ({lanes} corsie)"
        return "rosso", 4, note, "no", lanes or 2, senso_unico

    if highway in ("secondary", "secondary_link") or lanes >= 3:
        note = f"strada secondaria trafficata"
        if lanes:
            note += f" ({lanes} corsie)"
        return "rosso", 4, note, "no", lanes or 2, senso_unico

    # Default: giallo for tertiary/residential/unclassified
    note = f"strada urbana senza ciclabile"
    if lanes:
        note += f" ({lanes} corsie)"
    return "giallo", 3, note, "no", lanes or 2, senso_unico


def guess_quartiere(tags, lat, lon):
    """Try to get suburb from addr tags or return generic based on position."""
    suburb = tags.get("addr:suburb", "") or tags.get("addr:quarter", "")
    if suburb:
        return suburb
    city_district = tags.get("addr:city_district", "")
    if city_district:
        return city_district
    return ""


def fetch_streets_overpass():
    """Fetch all named streets in Rome from Overpass API."""
    print("Fetching streets from Overpass API (this may take a while)...")

    highway_filter = "|".join(RELEVANT_HIGHWAYS - SKIP_HIGHWAYS)

    query = f"""
[out:json][timeout:180];
area["name"="Roma"]["admin_level"="8"]->.roma;
(
  way["highway"~"^({highway_filter})$"]["name"](area.roma);
);
out tags center;
"""

    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(
        OVERPASS_URL,
        data=data,
        headers={"User-Agent": USER_AGENT},
    )

    try:
        with urllib.request.urlopen(req, timeout=200) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Overpass error: {e}")
        sys.exit(1)

    elements = result.get("elements", [])
    print(f"Received {len(elements)} way elements from Overpass")
    return elements


def deduplicate_streets(elements):
    """
    Group ways by street name, pick the most informative tags.
    Returns dict of {name: best_tags_and_center}.
    """
    by_name = defaultdict(list)
    for el in elements:
        name = el.get("tags", {}).get("name", "").strip()
        if not name:
            continue
        by_name[name].append(el)

    streets = {}
    for name, ways in by_name.items():
        best = ways[0]
        best_tag_count = len(best.get("tags", {}))
        for w in ways[1:]:
            tc = len(w.get("tags", {}))
            if tc > best_tag_count:
                best = w
                best_tag_count = tc

        center = best.get("center", {})
        streets[name] = {
            "tags": best.get("tags", {}),
            "lat": center.get("lat", 0),
            "lon": center.get("lon", 0),
            "way_count": len(ways),
        }

    return streets


def municipio_from_coords(lat, lon):
    """Rough municipio estimation from coordinates."""
    # Very rough mapping based on Rome's geography
    if lat > 41.93 and lon < 12.45:
        return "XIV"
    if lat > 41.93 and lon >= 12.45 and lon < 12.52:
        return "III"
    if lat > 41.93 and lon >= 12.52:
        return "IV"
    if lat > 41.88 and lat <= 41.93 and lon < 12.42:
        return "XIII"
    if lat > 41.88 and lat <= 41.93 and lon >= 12.42 and lon < 12.47:
        return "I"
    if lat > 41.88 and lat <= 41.93 and lon >= 12.47 and lon < 12.52:
        return "II"
    if lat > 41.88 and lat <= 41.93 and lon >= 12.52:
        return "V"
    if lat > 41.83 and lat <= 41.88 and lon < 12.45:
        return "XII"
    if lat > 41.83 and lat <= 41.88 and lon >= 12.45 and lon < 12.52:
        return "IX"
    if lat > 41.83 and lat <= 41.88 and lon >= 12.52:
        return "VII"
    if lat <= 41.83 and lon < 12.40:
        return "XI"
    if lat <= 41.83 and lon >= 12.40 and lon < 12.52:
        return "VIII"
    if lat <= 41.83:
        return "VI"
    return "I"


def main():
    print("=" * 60)
    print("StreetSmart — Importazione bulk strade da OpenStreetMap")
    print("=" * 60)

    existing = load_existing_names()
    print(f"Strade già nel database: {len(existing)}")

    last_id = get_last_id()
    print(f"Ultimo ID: SS-ROM-{last_id:04d}")

    elements = fetch_streets_overpass()
    streets = deduplicate_streets(elements)
    print(f"Strade uniche trovate: {len(streets)}")

    # Filter out existing
    new_streets = {}
    for name, data in streets.items():
        clean = name.lower().strip()
        clean = re.sub(r'\s*\(.*?\)', '', clean).strip()
        if clean not in existing:
            new_streets[name] = data

    print(f"Nuove strade (non nel database): {len(new_streets)}")

    if not new_streets:
        print("Nessuna nuova strada da importare!")
        return

    # Classify and write CSV
    rows = []
    next_id = last_id + 1

    for name, data in sorted(new_streets.items()):
        tags = data["tags"]
        highway = tags.get("highway", "")

        if highway in SKIP_HIGHWAYS:
            continue

        classificazione, score, note, ciclabile, n_corsie, senso_unico = classify_street(tags)
        quartiere = guess_quartiere(tags, data["lat"], data["lon"])
        municipio = municipio_from_coords(data["lat"], data["lon"])

        row = {
            "id": f"SS-ROM-{next_id:04d}",
            "nome": name,
            "quartiere": quartiere or f"Municipio Roma {municipio}",
            "classificazione": classificazione,
            "score": score,
            "note": note,
            "ciclabile_presente": ciclabile,
            "n_corsie": n_corsie,
            "senso_unico": senso_unico,
            "n_testimonianze": 0,
            "municipio": municipio,
            "data_segnalazione": "2026-06-27",
        }
        rows.append(row)
        next_id += 1

    # Write output CSV
    fieldnames = ["id", "nome", "quartiere", "classificazione", "score",
                  "note", "ciclabile_presente", "n_corsie", "senso_unico",
                  "n_testimonianze", "municipio", "data_segnalazione"]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Stats
    by_class = defaultdict(int)
    for r in rows:
        by_class[r["classificazione"]] += 1

    print(f"\n{'=' * 60}")
    print(f"RISULTATO: {len(rows)} nuove strade classificate")
    print(f"{'=' * 60}")
    for cls in ["nero", "rosso", "giallo", "verde", "blu"]:
        print(f"  {cls:12s}: {by_class.get(cls, 0):5d}")
    print(f"  {'TOTALE':12s}: {len(rows):5d}")
    print(f"\nFile salvato: {OUTPUT_CSV}")
    print(f"Prossimo ID: SS-ROM-{next_id:04d}")
    print(f"\nPer aggiungere al database master:")
    print(f"  tail -n +2 {OUTPUT_CSV} >> {MASTER_CSV}")
    print(f"  python scripts/build.py")


if __name__ == "__main__":
    main()
