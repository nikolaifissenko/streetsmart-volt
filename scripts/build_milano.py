#!/usr/bin/env python3
"""
build_milano.py — Come build_city.py, ma per Milano usa query Overpass
divise per griglia geografica invece che un'unica query sull'intera area
amministrativa.

Motivo: una query [out:json] su area["name"="Milano"]["admin_level"="8"]
con "out geom" su tutte le strade rilevanti va in timeout/504 su tutti i
mirror Overpass provati (vedi nota in CLAUDE.md, sezione Altre città) — il
comune di Milano ha ~33k way OSM rilevanti da restituire in un colpo solo.
Qui la stessa area viene interrogata a pezzi (bbox grid), ogni pezzo con
un payload piccolo abbastanza da rispondere in tempo, poi i risultati
vengono uniti deduplicando per id way (i way vicini ai bordi di due celle
vengono restituiti da entrambe le query).

Riusa la logica di classificazione/raggruppamento/tiling di build_city.py.

Uso:
    python scripts/build_milano.py
"""
import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from build_city import (
    RELEVANT_HIGHWAYS, SKIP_HIGHWAYS, OVERPASS_URLS, USER_AGENT,
    TARGET_FEATURES_PER_TILE,
    group_by_name, merge_geometry, classify_group, best_tags, grid_cell,
)

ROOT = Path(__file__).parent.parent
CITY_NAME = "Milano"
PREFIX = "MIL"
SLUG = "milano"

# Bounding box del comune di Milano (relation OSM 44915, admin_level=8),
# letto via Overpass `out bb;` su rel["name"="Milano"]["admin_level"="8"].
BBOX = (45.3867381, 9.0408867, 45.5358482, 9.2781103)  # minlat, minlon, maxlat, maxlon
GRID_COLS = 4
GRID_ROWS = 4


def fetch_bbox(south, west, north, east):
    highway_filter = "|".join(RELEVANT_HIGHWAYS - SKIP_HIGHWAYS)
    query = f"""
[out:json][timeout:120];
(
  way["highway"~"^({highway_filter})$"]["name"]({south},{west},{north},{east});
);
out geom;
"""
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    last_err = None
    for url in OVERPASS_URLS:
        req = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=140) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            return result.get("elements", [])
        except Exception as e:
            print(f"    mirror {url} fallita ({e}), provo la successiva...")
            last_err = e
    raise last_err


def fetch_milano_ways():
    min_lat, min_lon, max_lat, max_lon = BBOX
    lat_step = (max_lat - min_lat) / GRID_ROWS
    lon_step = (max_lon - min_lon) / GRID_COLS

    by_id = {}
    total_cells = GRID_ROWS * GRID_COLS
    cell_n = 0
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            cell_n += 1
            south = min_lat + row * lat_step
            north = min_lat + (row + 1) * lat_step
            west = min_lon + col * lon_step
            east = min_lon + (col + 1) * lon_step
            print(f"  Cella {cell_n}/{total_cells} ({south:.4f},{west:.4f},{north:.4f},{east:.4f})...")
            elements = fetch_bbox(south, west, north, east)
            new = 0
            for el in elements:
                if el.get("id") not in by_id:
                    by_id[el["id"]] = el
                    new += 1
            print(f"    {len(elements)} way ricevuti, {new} nuovi (totale finora: {len(by_id)})")
    return list(by_id.values())


def main():
    out_dir = ROOT / "cities" / SLUG
    tiles_dir = out_dir / "tiles"
    tiles_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"StreetSmart — build automatico per {CITY_NAME} (bbox grid {GRID_ROWS}x{GRID_COLS})")
    print("=" * 60)
    elements = fetch_milano_ways()
    print(f"\nTotale way unici ricevuti da OSM: {len(elements)}")

    by_name = group_by_name(elements)
    print(f"Nomi di strade unici: {len(by_name)}")

    if not by_name:
        print("Nessuna strada trovata.")
        sys.exit(1)

    import csv
    import math
    from collections import defaultdict

    features = []
    next_id = 1
    for name in sorted(by_name):
        ways = by_name[name]
        geom = merge_geometry(ways)
        if not geom:
            continue
        classificazione, score, note, ciclabile, n_corsie, senso_unico = classify_group(ways)
        tags = best_tags(ways)

        coords = geom["coordinates"] if geom["type"] == "LineString" else geom["coordinates"][0]
        clat = sum(c[1] for c in coords) / len(coords)
        clon = sum(c[0] for c in coords) / len(coords)

        quartiere = tags.get("addr:suburb", "") or tags.get("addr:quarter", "") or tags.get("addr:city_district", "")
        sid = f"SS-{PREFIX}-{next_id:04d}"
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

    csv_path = out_dir / f"streetsmart_{SLUG}.csv"
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
    print(f"{len(features)} strade classificate ({CITY_NAME})")
    for cls in ["nero", "rosso", "giallo", "verde", "blu"]:
        print(f"  {cls:8s}: {counts.get(cls, 0)}")
    print(f"Zone geografiche: {len(by_cell)} ({tiles_dir})")
    print(f"CSV: {csv_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
