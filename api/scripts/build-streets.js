#!/usr/bin/env node
// Preprocessa il GeoJSON in un formato compatto per il Worker.
// Output: src/streets-data.js — array di segmenti con bounding box per ricerca veloce.

const fs = require('fs');
const path = require('path');

const geojson = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../../streetsmart_roma.geojson'), 'utf8')
);

const streets = [];

for (const feature of geojson.features) {
  const p = feature.properties;
  const coords = feature.geometry.type === 'MultiLineString'
    ? feature.geometry.coordinates.flat()
    : feature.geometry.coordinates;

  if (!coords || coords.length === 0) continue;

  let minLon = Infinity, maxLon = -Infinity, minLat = Infinity, maxLat = -Infinity;
  for (const [lon, lat] of coords) {
    if (lon < minLon) minLon = lon;
    if (lon > maxLon) maxLon = lon;
    if (lat < minLat) minLat = lat;
    if (lat > maxLat) maxLat = lat;
  }

  // Centroid approssimato
  const cLon = (minLon + maxLon) / 2;
  const cLat = (minLat + maxLat) / 2;

  streets.push({
    id: p.id,
    nome: p.nome,
    quartiere: p.quartiere,
    municipio: p.municipio,
    classificazione: p.classificazione,
    score: p.score,
    ciclabile: p.ciclabile,
    n_corsie: p.n_corsie,
    segments: coords,
    bbox: [minLon, minLat, maxLon, maxLat],
    centroid: [cLon, cLat],
  });
}

const out = `export const STREETS = ${JSON.stringify(streets)};\n`;
fs.writeFileSync(path.join(__dirname, '../src/streets-data.js'), out);
console.log(`Built ${streets.length} streets for API`);
