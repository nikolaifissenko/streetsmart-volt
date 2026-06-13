# Scripts — StreetSmart

- `build.py` — converte `data/master/streetsmart_roma_completo.csv` in
  `dist/streetsmart_roma.geojson`, geocodificando via Nominatim/OSM
  (cache in `data/master/.geocode_cache.json`)
- `validate.py` — controlla integrità del CSV master (campi obbligatori,
  ID univoci, classificazione/score coerenti)
- `stats.py` — genera `docs/stats.md` e `docs/stats.json` con statistiche
  aggregate (totali, per municipio, % pericolose/ciclabili)
- `export_api.py` — genera `dist/api/strade.json` e `dist/api/municipi/*.json`
  come snapshot API REST statica
- `generate_one_pager.py` — genera `docs/one_pager_tech.md` (pitch B2B) da
  `docs/stats.json`
- `import_segnalazioni.py` — converte un export CSV di Formspree (form
  segnalazione) in righe pronte da appendere al master

Tutti gli script (tranne `import_segnalazioni.py`, manuale) sono eseguiti
automaticamente dalla CI (`.github/workflows/build-geojson.yml`) ad ogni
push che modifica il master CSV.

I PDF (municipio1.pdf, municipio2.pdf, municipio3.pdf, one_pager_tech.pdf, liberatoria.pdf)
sono in docs/pdf/ — copiati manualmente perché binari.
