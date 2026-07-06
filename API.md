# StreetSmart API (commercial)

Authenticated bulk/filtered access to the street danger dataset, for
licensed customers. The public PWA doesn't use this — it reads the
unauthenticated tiles directly (see `tiles/` in CLAUDE.md). This API
sits in front of the same tiles and adds an API key, query filtering,
and a single combined response.

Implementation: `worker/` (Cloudflare Worker). It has no database of
its own — it fetches and merges the same `tiles/*.geojson` files the
PWA serves, so a customer's data is always as fresh as the map.

## Endpoint

```
GET https://<your-worker-subdomain>.workers.dev/streets
```

### Auth

Send the API key as either:

```
X-API-Key: <key>
```
or
```
Authorization: Bearer <key>
```

Missing/invalid key → `401`.

### Query params (all optional, combine freely)

| Param | Example | Effect |
|---|---|---|
| `municipio` | `municipio=I,II` | Only these municipi (comma-separated Roman numerals) |
| `classificazione` | `classificazione=nero,rosso` | Only these classes |
| `bbox` | `bbox=12.45,41.88,12.50,41.92` | Only streets with a point inside `minLon,minLat,maxLon,maxLat` |

No params → the full dataset (15,090 streets).

### Response

A GeoJSON `FeatureCollection`, same feature shape as the public tiles
(`id`, `nome`, `quartiere`, `classificazione`, `score`, `municipio`,
etc. + geometry).

### Example

```bash
curl "https://streetsmart-api.<subdomain>.workers.dev/streets?municipio=I&classificazione=nero,rosso" \
  -H "X-API-Key: $KEY"
```

## Operating it

Deploy (one-time, requires a free Cloudflare account):

```bash
cd worker
npm install
npx wrangler login
npx wrangler secret put API_KEYS   # paste a comma-separated list of valid keys
npx wrangler deploy
```

To add or revoke a customer, update the secret and redeploy isn't
needed — just:

```bash
npx wrangler secret put API_KEYS
```
(paste the full new comma-separated list; there's no per-key add/remove,
you replace the whole list each time)

Local dev (no Cloudflare account needed):

```bash
cd worker
npm install
npx wrangler dev
# API_KEYS for local testing comes from worker/.dev.vars (gitignored)
```

## Known limitations (fine for launch, revisit if volume grows)

- No rate limiting — add a Cloudflare rate-limiting rule if a key gets abused.
- No per-key usage tracking/billing — it's a flat allow/deny list.
- No self-serve signup — keys are issued by hand.
