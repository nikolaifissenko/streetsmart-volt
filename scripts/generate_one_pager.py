#!/usr/bin/env python3
"""
StreetSmart generate_one_pager.py
Genera docs/one_pager_tech.md a partire da docs/stats.json:
un riassunto sintetico (1 pagina) del database, pensato per
pitch B2B a operatori di micromobilita (Lime, Dott, Tier), Comuni,
app di navigazione.

Esegui prima scripts/stats.py per aggiornare docs/stats.json.

Uso: python scripts/generate_one_pager.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
STATS_JSON = ROOT / "docs" / "stats.json"
OUTPUT_MD = ROOT / "docs" / "one_pager_tech.md"

ROMAN_NAMES = {
    "I": "Centro Storico", "II": "Parioli/Flaminio/Salario",
    "III": "Montesacro", "IV": "Tiburtina", "V": "Prenestino/Centocelle",
    "VII": "Appio Latino/Tuscolano", "VIII": "Appia Antica/Ostiense",
    "IX": "EUR/Laurentino", "XI": "Portuense/Magliana",
    "XII": "Monteverde/Gianicolense", "XIII": "Aurelio",
    "XIV": "Monte Mario", "XV": "Cassia/Flaminia",
}


def main():
    if not STATS_JSON.exists():
        print(f"ERRORE: {STATS_JSON} non trovato — esegui prima scripts/stats.py")
        return

    with open(STATS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    total = data["strade_totali"]
    by_class = data["distribuzione_classificazioni"]
    pericolose = by_class.get("rosso", 0) + by_class.get("nero", 0)
    ciclabili = by_class.get("verde", 0) + by_class.get("verde-giallo", 0) + by_class.get("verde-blu", 0)

    pct_pericolose = round(100 * pericolose / total, 1)
    pct_ciclabili = round(100 * ciclabili / total, 1)

    municipi_sorted = sorted(data["per_municipio"], key=lambda m: -m["pct_pericolose"])
    top_pericolosi = municipi_sorted[:3]

    lines = []
    lines.append("# StreetSmart — One Pager Tech")
    lines.append("")
    lines.append(f"_Aggiornato il {data['generato_il']}_")
    lines.append("")
    lines.append("## Cos'è")
    lines.append("")
    lines.append(
        "StreetSmart è il database B2B delle strade di Roma classificate per "
        "pericolosità ciclistica, costruito da una community di Sentinelle e "
        "verificato manualmente. Vendibile a operatori di micromobilità "
        "(Lime, Dott, Tier), Comuni e app di navigazione per ottimizzare "
        "routing e sicurezza dei ciclisti/monopattini."
    )
    lines.append("")
    lines.append("## Numeri chiave")
    lines.append("")
    lines.append(f"- **{total} strade** classificate a Roma")
    lines.append(f"- **{pct_pericolose}%** delle strade è ad alto rischio (rosso/nero)")
    lines.append(f"- **{pct_ciclabili}%** ha una ciclabile presente (verde)")
    lines.append(f"- Copertura: {len(data['per_municipio'])} municipi")
    lines.append("")
    lines.append("## Distribuzione classificazioni")
    lines.append("")
    lines.append("| Classificazione | Strade | % |")
    lines.append("|---|---|---|")
    for cls, count in sorted(by_class.items(), key=lambda x: -x[1]):
        pct = round(100 * count / total, 1)
        lines.append(f"| {cls} | {count} | {pct}% |")
    lines.append("")
    lines.append("## Municipi a maggior rischio")
    lines.append("")
    lines.append("| Municipio | Zona | Strade | % pericolose |")
    lines.append("|---|---|---|---|")
    for m in top_pericolosi:
        zona = ROMAN_NAMES.get(m["municipio"], "")
        lines.append(f"| {m['municipio']} | {zona} | {m['totale']} | {m['pct_pericolose']}% |")
    lines.append("")
    lines.append("## Formato dati")
    lines.append("")
    lines.append(
        "CSV (source of truth) e GeoJSON/JSON via API statica "
        "(`dist/streetsmart_roma.geojson`, `dist/api/strade.json`), "
        "aggiornati automaticamente via CI ad ogni nuova segnalazione."
    )
    lines.append("")
    lines.append("## Community Sentinelle")
    lines.append("")
    lines.append(
        "Obiettivo: 100 Sentinelle attive per la raccolta dati, poi il "
        "database viene proposto alle istituzioni comunali."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("Contatti: Instagram [@streetsmart.nav](https://instagram.com/streetsmart.nav)")
    lines.append("")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Scritto {OUTPUT_MD}")


if __name__ == "__main__":
    main()
