#!/usr/bin/env python3
"""
build_city.py — Costruisce un dataset di strade classificate per una città
diversa da Roma, usando solo tag OSM (classificazione automatica, nessuna
revisione manuale/testimonianza come per le 574 strade curate a mano di Roma).

Riusa la stessa logica di classificazione di import_osm_bulk.py:
- NERO (5): highway=trunk/primary + lanes>=4, o maxspeed>=70
- ROSSO (4): highway=primary/secondary senza ciclabile, o lanes>=3
- GIALLO (3): highway=tertiary/residential/unclassified senza ciclabile
- VERDE (1): cycleway presente
- BLU (2): highway=pedestrian/living_street, o access=no/private (ZTL)

A differenza di Roma, qui non esistono "municipi" ufficiali da usare per i
tile — le strade vengono raggruppate in una griglia geografica generata
dinamicamente (zona-A1, zona-A2, ...), così lo script funziona per
qualunque città senza conoscere i suoi confini amministrativi.

Uso:
    python scripts/build_city.py "Napoli" NAP

Genera in cities/<slug>/:
    streetsmart_<slug>.csv   — CSV in stile Roma, per revisione/estensione futura
    tiles/zona-*.geojson     — tile geografici
    tiles/index.json         — elenco slug zona
"""
import csv
import json
import math
import re
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).parent.parent
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "StreetSmart-Import/1.0 (nikolaifissenko@github)"
TARGET_FEATURES_PER_TILE = 1000

RELEVANT_HIGHWAYS = {
    "motorway", "trunk", "primary", "secondary", "tertiary",
    "residential", "unclassified", "living_street", "pedestrian",
    "cycleway", "service",
}
SKIP_HIGHWAYS = {"motorway", "motorway_link", "service"}


def classify_street(tags):
    """Stessa logica di scripts/import_osm_bulk.py:classify_street."""
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

    if has_cycleway:
        return "verde", 1, "ciclabile presente (da OpenStreetMap)", "si", lanes or 2, senso_unico

    if is_pedestrian or is_ztl:
        note = "zona pedonale / living street" if is_pedestrian else "accesso limitato (ZTL)"
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
            return "nero", 5, f"strada principale {lanes} corsie senza protezione ciclabile", "no", lanes, senso_unico
        note = "strada principale trafficata" + (f" ({lanes} corsie)" if lanes else "")
        return "rosso", 4, note, "no", lanes or 2, senso_unico

    if highway in ("secondary", "secondary_link") or lanes >= 3:
        note = "strada secondaria trafficata" + (f" ({lanes} corsie)" if lanes else "")
        return "rosso", 4, note, "no", lanes or 2, senso_unico

    note = "strada urbana senza ciclabile" + (f" ({lanes} corsie)" if lanes else "")
    return "giallo", 3, note, "no", lanes or 2, senso_unico


def fetch_city_ways(city_name, admin_level=8):
    highway_filter = "|".join(RELEVANT_HIGHWAYS - SKIP_HIGHWAYS)
    query = f"""
[out:json][timeout:300];
area["name"="{city_name}"]["admin_level"="{admin_level}"]->.city;
(
  way["highway"~"^({highway_filter})$"]["name"](area.city);
);
out geom;
"""
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(OVERPASS_URL, data=data, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=320) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result.get("elements", [])


def group_by_name(elements):
    by_name = defaultdict(list)
    for el in elements:
        name = el.get("tags", {}).get("name", "").strip()
        if name and el.get("geometry"):
            by_name[name].append(el)
    return by_name


def merge_geometry(ways):
    lines = []
    for w in ways:
        coords = [[pt["lon"], pt["lat"]] for pt in w.get("geometry", [])]
        if len(coords) >= 2:
            lines.append(coords)
    if not lines:
        return None
    if len(lines) == 1:
        return {"type": "LineString", "coordinates": lines[0]}
    return {"type": "MultiLineString", "coordinates": lines}


DANGER_ORDER = {"nero": 5, "rosso": 4, "giallo": 3, "blu": 2, "verde": 1}


def classify_group(ways):
    """
    A named street is often split into many OSM ways with inconsistent tags
    (e.g. one stretch tagged highway=pedestrian, another highway=secondary).
    Picking "the way with the most tags" is arbitrary and can pick an
    unrepresentative segment. Instead, classify every segment and take
    the classification most of them agree on, breaking ties toward the
    more dangerous class (same conservative bias as the Rome ruleset).
    """
    results = [classify_street(w.get("tags", {})) for w in ways]
    votes = Counter(r[0] for r in results)
    max_count = max(votes.values())
    winners = [cls for cls, count in votes.items() if count == max_count]
    winner = max(winners, key=lambda c: DANGER_ORDER[c])
    for r in results:
        if r[0] == winner:
            return r
    return results[0]


def best_tags(ways):
    """Representative tags for metadata (addr:*) only — not used for classification."""
    best = ways[0]
    for w in ways[1:]:
        if len(w.get("tags", {})) > len(best.get("tags", {})):
            best = w
    return best.get("tags", {})


def grid_cell(lat, lon, bounds, cols, rows):
    min_lat, max_lat, min_lon, max_lon = bounds
    col = int((lon - min_lon) / (max_lon - min_lon) * cols) if max_lon > min_lon else 0
    row = int((lat - min_lat) / (max_lat - min_lat) * rows) if max_lat > min_lat else 0
    col = min(cols - 1, max(0, col))
    row = min(rows - 1, max(0, row))
    return f"{chr(ord('A') + row)}{col + 1}"


def main():
    if len(sys.argv) < 3:
        print("Uso: python scripts/build_city.py <NomeCittaOSM> <PREFISSO_ID>")
        print('Esempio: python scripts/build_city.py "Napoli" NAP')
        sys.exit(1)

    city_name = sys.argv[1]
    prefix = sys.argv[2].upper()
    slug = re.sub(r'[^a-z0-9]+', '-', city_name.lower()).strip('-')

    out_dir = ROOT / "cities" / slug
    tiles_dir = out_dir / "tiles"
    tiles_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"StreetSmart — build automatico per {city_name}")
    print("=" * 60)
    print(f"Fetching da Overpass (puo' richiedere alcuni minuti)...")
    elements = fetch_city_ways(city_name)
    print(f"Ricevuti {len(elements)} way da OSM")

    by_name = group_by_name(elements)
    print(f"Nomi di strade unici: {len(by_name)}")

    if not by_name:
        print("Nessuna strada trovata — controlla il nome della città su OSM (area/admin_level).")
        sys.exit(1)

    features = []
    next_id = 1
    for name in sorted(by_name):
        ways = by_name[name]
        geom = merge_geometry(ways)
        if not geom:
            continue
        classificazione, score, note, ciclabile, n_corsie, senso_unico = classify_group(ways)
        tags = best_tags(ways)  # just for metadata (addr:*), not classification

        coords = geom["coordinates"] if geom["type"] == "LineString" else geom["coordinates"][0]
        clat = sum(c[1] for c in coords) / len(coords)
        clon = sum(c[0] for c in coords) / len(coords)

        quartiere = tags.get("addr:suburb", "") or tags.get("addr:quarter", "") or tags.get("addr:city_district", "")
        sid = f"SS-{prefix}-{next_id:04d}"
        next_id += 1

        features.append({
            "type": "Feature",
            "properties": {
                "id": sid, "nome": name, "quartiere": quartiere,
                "classificazione": classificazione, "score": score, "note": note,
                "ciclabile": ciclabile, "n_corsie": str(n_corsie), "senso_unico": senso_unico,
                "n_testimonianze": "0", "zona": None,
            },
            "geometry": geom,
            "_centroid": (clat, clon),
        })

    lats = [f["_centroid"][0] for f in features]
    lons = [f["_centroid"][1] for f in features]
    min_lat, max_lat, min_lon, max_lon = min(lats), max(lats), min(lons), max(lons)

    n_cells = max(1, round(len(features) / TARGET_FEATURES_PER_TILE))
    cols = max(1, round(math.sqrt(n_cells)))
    rows_n = max(1, math.ceil(n_cells / cols))

    by_cell = defaultdict(list)
    for f in features:
        clat, clon = f.pop("_centroid")
        cell = grid_cell(clat, clon, (min_lat, max_lat, min_lon, max_lon), cols, rows_n)
        f["properties"]["zona"] = cell
        by_cell[cell].append(f)

    for cell, feats in by_cell.items():
        with open(tiles_dir / f"zona-{cell}.geojson", "w", encoding="utf-8") as fh:
            json.dump({"type": "FeatureCollection", "features": feats}, fh, ensure_ascii=False)
    with open(tiles_dir / "index.json", "w", encoding="utf-8") as fh:
        json.dump(sorted(by_cell.keys()), fh)

    csv_path = out_dir / f"streetsmart_{slug}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "nome", "quartiere", "classificazione", "score", "note",
                    "ciclabile_presente", "n_corsie", "senso_unico", "n_testimonianze",
                    "zona", "data_segnalazione"])
        for f in features:
            p = f["properties"]
            w.writerow([p["id"], p["nome"], p["quartiere"], p["classificazione"], p["score"],
                        p["note"], p["ciclabile"], p["n_corsie"], p["senso_unico"],
                        p["n_testimonianze"], p["zona"], ""])

    counts = Counter(f["properties"]["classificazione"] for f in features)
    print(f"\n{'=' * 60}")
    print(f"{len(features)} strade classificate ({city_name})")
    for cls in ["nero", "rosso", "giallo", "verde", "blu"]:
        print(f"  {cls:8s}: {counts.get(cls, 0)}")
    print(f"Zone geografiche: {len(by_cell)} ({tiles_dir})")
    print(f"CSV: {csv_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
