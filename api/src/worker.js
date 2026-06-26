import { STREETS } from './streets-data.js';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS_HEADERS },
  });
}

// Distanza punto-segmento in gradi (approssimata, sufficiente per ranking)
function distToSegment(px, py, ax, ay, bx, by) {
  const dx = bx - ax, dy = by - ay;
  const lenSq = dx * dx + dy * dy;
  if (lenSq === 0) return Math.hypot(px - ax, py - ay);
  let t = ((px - ax) * dx + (py - ay) * dy) / lenSq;
  t = Math.max(0, Math.min(1, t));
  return Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
}

function findNearest(lon, lat, radius = 0.003) {
  let best = null;
  let bestDist = Infinity;

  for (const street of STREETS) {
    const [minLon, minLat, maxLon, maxLat] = street.bbox;
    if (lon < minLon - radius || lon > maxLon + radius ||
        lat < minLat - radius || lat > maxLat + radius) continue;

    const segs = street.segments;
    for (let i = 0; i < segs.length - 1; i++) {
      const d = distToSegment(lon, lat, segs[i][0], segs[i][1], segs[i + 1][0], segs[i + 1][1]);
      if (d < bestDist) {
        bestDist = d;
        best = street;
      }
    }
  }
  return best ? { street: best, distance_deg: bestDist } : null;
}

// Gradi → metri approssimativi a Roma (lat ~41.9)
function degToMeters(deg) {
  return deg * 111320 * Math.cos(41.9 * Math.PI / 180);
}

function handleScore(url) {
  const lat = parseFloat(url.searchParams.get('lat'));
  const lon = parseFloat(url.searchParams.get('lon'));
  if (isNaN(lat) || isNaN(lon)) {
    return json({ error: 'Parametri lat e lon richiesti' }, 400);
  }

  const result = findNearest(lon, lat);
  if (!result) {
    return json({ error: 'Nessuna strada trovata nelle vicinanze' }, 404);
  }

  const s = result.street;
  return json({
    id: s.id,
    nome: s.nome,
    quartiere: s.quartiere,
    municipio: s.municipio,
    classificazione: s.classificazione,
    score: s.score,
    ciclabile: s.ciclabile,
    n_corsie: s.n_corsie,
    distanza_m: Math.round(degToMeters(result.distance_deg)),
  });
}

function handleRoute(url) {
  const from = url.searchParams.get('from');
  const to = url.searchParams.get('to');
  if (!from || !to) {
    return json({ error: 'Parametri from e to richiesti (formato: lat,lon)' }, 400);
  }

  const [fromLat, fromLon] = from.split(',').map(Number);
  const [toLat, toLon] = to.split(',').map(Number);
  if ([fromLat, fromLon, toLat, toLon].some(isNaN)) {
    return json({ error: 'Formato coordinate non valido. Usa: lat,lon' }, 400);
  }

  // Campiona punti lungo la linea retta e calcola score medio
  const SAMPLES = 10;
  const scores = [];
  const strade = [];

  for (let i = 0; i <= SAMPLES; i++) {
    const t = i / SAMPLES;
    const lat = fromLat + t * (toLat - fromLat);
    const lon = fromLon + t * (toLon - fromLon);
    const result = findNearest(lon, lat);
    if (result && degToMeters(result.distance_deg) < 100) {
      scores.push(result.street.score);
      const id = result.street.id;
      if (!strade.find(s => s.id === id)) {
        strade.push({
          id: result.street.id,
          nome: result.street.nome,
          classificazione: result.street.classificazione,
          score: result.street.score,
        });
      }
    }
  }

  if (scores.length === 0) {
    return json({ error: 'Nessuna strada trovata lungo il percorso' }, 404);
  }

  const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
  const max = Math.max(...scores);

  return json({
    score_medio: Math.round(avg * 10) / 10,
    score_massimo: max,
    n_strade: strade.length,
    strade,
  });
}

function handleStats() {
  const counts = { nero: 0, rosso: 0, giallo: 0, verde: 0, blu: 0 };
  for (const s of STREETS) {
    if (counts[s.classificazione] !== undefined) counts[s.classificazione]++;
  }
  return json({
    totale_strade: STREETS.length,
    per_classificazione: counts,
    versione: '1.0.0',
  });
}

function handleDocs() {
  return json({
    name: 'StreetSmart API',
    version: '1.0.0',
    description: 'API per il danger score delle strade di Roma per la micromobilità',
    endpoints: {
      'GET /v1/score': {
        params: { lat: 'number', lon: 'number' },
        example: '/v1/score?lat=41.8902&lon=12.4922',
      },
      'GET /v1/route': {
        params: { from: 'lat,lon', to: 'lat,lon' },
        example: '/v1/route?from=41.8902,12.4922&to=41.9028,12.4964',
      },
      'GET /v1/stats': {
        params: {},
        description: 'Statistiche del database',
      },
    },
  });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    const path = url.pathname;

    if (path === '/' || path === '/v1') return handleDocs();
    if (path === '/v1/score') return handleScore(url);
    if (path === '/v1/route') return handleRoute(url);
    if (path === '/v1/stats') return handleStats();

    return json({ error: 'Endpoint non trovato. Visita / per la documentazione.' }, 404);
  },
};
