/**
 * StreetSmart commercial API — Cloudflare Worker.
 *
 * Gates a bulk/filterable export of the street dataset behind an API key,
 * for paying licensees. The public PWA keeps reading the unauthenticated
 * per-municipio tiles directly from GitHub Pages; this Worker just adds
 * auth + query filtering + a single combined response on top of the same
 * tiles, so the data behind the paid tier is always in sync with the map.
 */

const TILES_BASE = 'https://nikolaifissenko.github.io/streetsmart-volt/tiles';
const CACHE_TTL_SECONDS = 300;

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'X-API-Key, Authorization, Content-Type',
  };
}

function jsonResponse(body, status, extraHeaders) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      ...corsHeaders(),
      ...(extraHeaders || {}),
    },
  });
}

function extractApiKey(request) {
  const headerKey = request.headers.get('X-API-Key');
  if (headerKey) return headerKey.trim();
  const auth = request.headers.get('Authorization') || '';
  const match = auth.match(/^Bearer\s+(.+)$/i);
  return match ? match[1].trim() : null;
}

function isValidKey(key, env) {
  if (!key || !env.API_KEYS) return false;
  const validKeys = env.API_KEYS.split(',').map((k) => k.trim()).filter(Boolean);
  return validKeys.includes(key);
}

function parseCsvParam(value) {
  if (!value) return null;
  return new Set(value.split(',').map((v) => v.trim()).filter(Boolean));
}

function parseBbox(value) {
  if (!value) return null;
  const parts = value.split(',').map(Number);
  if (parts.length !== 4 || parts.some(Number.isNaN)) return null;
  const [minLon, minLat, maxLon, maxLat] = parts;
  return { minLon, minLat, maxLon, maxLat };
}

function geometryIntersectsBbox(geometry, bbox) {
  if (!geometry) return false;
  const coordSets =
    geometry.type === 'LineString' ? [geometry.coordinates] : geometry.coordinates;
  for (const line of coordSets) {
    for (const [lon, lat] of line) {
      if (lon >= bbox.minLon && lon <= bbox.maxLon && lat >= bbox.minLat && lat <= bbox.maxLat) {
        return true;
      }
    }
  }
  return false;
}

async function fetchTileIndex() {
  const res = await fetch(`${TILES_BASE}/index.json`, { cf: { cacheTtl: CACHE_TTL_SECONDS, cacheEverything: true } });
  if (!res.ok) throw new Error(`tile index fetch failed: HTTP ${res.status}`);
  return res.json();
}

async function fetchTile(slug) {
  const res = await fetch(`${TILES_BASE}/municipio-${encodeURIComponent(slug)}.geojson`, {
    cf: { cacheTtl: CACHE_TTL_SECONDS, cacheEverything: true },
  });
  if (!res.ok) throw new Error(`tile fetch failed for ${slug}: HTTP ${res.status}`);
  return res.json();
}

async function handleStreets(request, env) {
  const key = extractApiKey(request);
  if (!isValidKey(key, env)) {
    return jsonResponse({ error: 'missing or invalid API key' }, 401);
  }

  const url = new URL(request.url);
  const municipioFilter = parseCsvParam(url.searchParams.get('municipio'));
  const classFilter = parseCsvParam(url.searchParams.get('classificazione'));
  const bbox = parseBbox(url.searchParams.get('bbox'));
  if (url.searchParams.has('bbox') && !bbox) {
    return jsonResponse({ error: 'bbox must be "minLon,minLat,maxLon,maxLat"' }, 400);
  }

  let slugs;
  try {
    slugs = await fetchTileIndex();
  } catch (err) {
    return jsonResponse({ error: 'upstream data unavailable', detail: err.message }, 502);
  }
  if (municipioFilter) {
    slugs = slugs.filter((s) => municipioFilter.has(s));
  }

  let tiles;
  try {
    tiles = await Promise.all(slugs.map(fetchTile));
  } catch (err) {
    return jsonResponse({ error: 'upstream data unavailable', detail: err.message }, 502);
  }

  let features = tiles.flatMap((t) => t.features);
  if (classFilter) {
    features = features.filter((f) => classFilter.has(f.properties.classificazione));
  }
  if (bbox) {
    features = features.filter((f) => geometryIntersectsBbox(f.geometry, bbox));
  }

  const body = { type: 'FeatureCollection', features };
  return jsonResponse(body, 200, {
    'Cache-Control': `private, max-age=${CACHE_TTL_SECONDS}`,
  });
}

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    const url = new URL(request.url);

    if (url.pathname === '/health') {
      return jsonResponse({ status: 'ok' }, 200);
    }

    if (url.pathname === '/streets' && request.method === 'GET') {
      return handleStreets(request, env);
    }

    return jsonResponse({ error: 'not found' }, 404);
  },
};
