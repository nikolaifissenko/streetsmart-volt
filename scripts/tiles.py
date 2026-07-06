#!/usr/bin/env python3
"""
tiles.py — Divide un FeatureCollection in tile per municipio.

La PWA non fetcha piu' un unico file con tutto il database (era
liberamente scaricabile in un colpo solo); fetcha invece i tile dei
singoli municipi elencati in tiles/index.json.

Nessuna chiamata di rete: opera sui feature gia' costruiti da
build.py / build_fast.py.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
TILES_DIR = ROOT / "tiles"


def municipio_slug(municipio):
    m = (municipio or "").strip()
    return m if m else "altro"


def write_tiles(features):
    by_muni = {}
    for feature in features:
        if not feature.get("geometry"):
            continue
        slug = municipio_slug(feature["properties"].get("municipio"))
        by_muni.setdefault(slug, []).append(feature)

    TILES_DIR.mkdir(exist_ok=True)
    for old in TILES_DIR.glob("municipio-*.geojson"):
        old.unlink()

    for slug, feats in by_muni.items():
        out = {"type": "FeatureCollection", "features": feats}
        with open(TILES_DIR / f"municipio-{slug}.geojson", "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)

    with open(TILES_DIR / "index.json", "w", encoding="utf-8") as f:
        json.dump(sorted(by_muni.keys()), f)

    print(f"Tile scritti: {len(by_muni)} municipi in {TILES_DIR}/")
    for slug, feats in sorted(by_muni.items(), key=lambda kv: -len(kv[1])):
        print(f"  municipio-{slug}.geojson: {len(feats)} strade")
