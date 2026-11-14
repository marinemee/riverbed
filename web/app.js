// Placeholder app. Real work: issues F1-F15. Demo basemap below is for development only: replace it (issue F1).
const map = new maplibregl.Map({
  container: 'map',
  style: 'https://demotiles.maplibre.org/style.json',
  center: [72.45, 34.9],
  zoom: 10,
});
map.addControl(new maplibregl.NavigationControl());

const slider = document.getElementById('rise');
const label = document.getElementById('rise-label');
const count = document.getElementById('count');
const note = document.getElementById('note');
let buildings = null;

async function loadBuildings() {
  try {
    const r = await fetch('data/buildings.geojson');
    buildings = await r.json();
  } catch (e) {
    buildings = null; // not exported yet: show a labelled placeholder, never fake numbers
  }
  update();
}

function update() {
  const h = parseFloat(slider.value);
  label.textContent = h.toFixed(1) + ' m above low-flow level';
  if (!buildings) { count.textContent = '\u2013'; return; }
  count.textContent = buildings.features.filter(f => f.properties.hand_min <= h).length;
}

slider.addEventListener('input', update);
map.on('load', loadBuildings);
