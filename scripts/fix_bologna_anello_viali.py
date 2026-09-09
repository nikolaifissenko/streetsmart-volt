"""Correzione una-tantum: l'anello dei viali di circonvallazione di Bologna
(i 12 viali che seguono il tracciato delle mura storiche) ha una pista
ciclabile — erano classificati rosso da build_city.py (classificazione OSM
automatica, nessuna ciclabile taggata). Segnalato da Nikolai da conoscenza
diretta del posto. Patcha sia il CSV sorgente sia i tile GeoJSON già
generati (stesso approccio di reconcile_segnalazioni_*.py).
"""
import csv
import json

RING_IDS = {
    "SS-BOL-1794", "SS-BOL-1768", "SS-BOL-1770", "SS-BOL-1783",
    "SS-BOL-1769", "SS-BOL-1772", "SS-BOL-1775", "SS-BOL-1782",
    "SS-BOL-1781", "SS-BOL-1779", "SS-BOL-1795", "SS-BOL-1771",
}

CSV_PATH = "cities/bologna/streetsmart_bologna.csv"
TILE_PATHS = ["cities/bologna/tiles/zona-A1.geojson", "cities/bologna/tiles/zona-B1.geojson"]

NEW_NOTE = "pista ciclabile presente sull'anello dei viali di circonvallazione"


def patch_csv():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        fieldnames = rows[0].keys()

    changed = 0
    for row in rows:
        if row["id"] in RING_IDS:
            row["classificazione"] = "verde"
            row["score"] = "1"
            row["note"] = NEW_NOTE
            row["ciclabile_presente"] = "si"
            changed += 1

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV: {changed} righe aggiornate")


def patch_tiles():
    for path in TILE_PATHS:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        changed = 0
        for feat in data["features"]:
            if feat["properties"].get("id") in RING_IDS:
                feat["properties"]["classificazione"] = "verde"
                feat["properties"]["score"] = 1
                feat["properties"]["note"] = NEW_NOTE
                feat["properties"]["ciclabile"] = "si"
                changed += 1
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        print(f"{path}: {changed} feature aggiornate")


if __name__ == "__main__":
    patch_csv()
    patch_tiles()
