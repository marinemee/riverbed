'use strict';

const el = Object.fromEntries([
  'controls', 'view', 'pass', 'pass-info', 'legend', 'corridor', 'buildings',
  'inundation', 'rise', 'rise-label', 'rise-min', 'rise-max', 'count', 'fit',
  'status', 'issues', 'validation', 'generated', 'credits', 'map-placeholder',
].map(id => [id, document.getElementById(id)]));
const state = {
  map: null, meta: null, coordinates: null, buildings: null, mask: null,
  images: new Map(), issues: new Map(), pending: new Set(),
  requests: { background: 0, inundation: 0 }, rasters: {},
};

function issue(key, message) {
  if (message) state.issues.set(key, message);
  else state.issues.delete(key);
  el.issues.replaceChildren(...[...state.issues.values()].map(text => {
    const item = document.createElement('li');
    item.textContent = text;
    return item;
  }));
}

function loading(key, active) {
  if (active) state.pending.add(key);
  else state.pending.delete(key);
  el.status.textContent = state.pending.size ? 'Loading selected layers…' :
    state.issues.size ? 'Some layers are unavailable; see details below.' : 'Exported layers ready.';
}

async function jsonFile(name) {
  const response = await fetch(`data/${name}`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`data/${name}: HTTP ${response.status}`);
  try { return await response.json(); }
  catch { throw new Error(`data/${name}: invalid JSON`); }
}

function checkMetadata(meta) {
  const b = meta.aoi_bbox;
  if (!Array.isArray(b) || b.length !== 4 || !b.every(Number.isFinite) ||
      b[0] >= b[2] || b[1] >= b[3] || b[0] < -180 || b[2] > 180 || b[1] < -90 || b[3] > 90) {
    throw new Error('data/meta.json: aoi_bbox must be [west, south, east, north] in EPSG:4326.');
  }
  if (meta.raster_crs && meta.raster_crs !== 'EPSG:4326') {
    throw new Error('data/meta.json: this map requires EPSG:4326 image overlays.');
  }
  if (!Array.isArray(meta.passes) || !meta.passes.length ||
      !meta.passes.every(pass => /^\d{8}$/.test(pass.id) && typeof pass.label === 'string') ||
      new Set(meta.passes.map(pass => pass.id)).size !== meta.passes.length) {
    throw new Error('data/meta.json: passes must contain unique dated IDs and labels.');
  }
  if (!Array.isArray(meta.rise_steps) || !meta.rise_steps.length ||
      !meta.rise_steps.every((rise, i, values) => Number.isFinite(rise) && rise >= 0 &&
        (i === 0 || rise > values[i - 1]))) {
    throw new Error('data/meta.json: rise_steps must be increasing numeric levels.');
  }
}

function rasterFile(name) {
  // sources maps exported PNG filenames to upstream TIFF paths. Only its keys
  // are web assets; the TIFF values must never be requested by the browser.
  if (state.meta.sources && !Object.hasOwn(state.meta.sources, name)) {
    throw new Error(`data/${name}: not declared in meta.json sources.`);
  }
  return name;
}

function imageFile(name) {
  if (!state.images.has(name)) {
    const promise = new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error(`data/${name}: image missing or unreadable.`));
      image.src = assetURL(name);
    });
    state.images.set(name, promise);
    // Keep decoded image memory bounded while the browser caches the PNG bytes.
    if (state.images.size > 4) state.images.delete(state.images.keys().next().value);
    promise.catch(() => state.images.delete(name));
  }
  return state.images.get(name);
}

function assetURL(name) {
  return `data/${name}?v=${encodeURIComponent(state.meta.generated || '')}`;
}

function removeRaster(slot) {
  const previous = state.rasters[slot];
  if (!previous) return;
  if (state.map.getLayer(previous.id)) state.map.removeLayer(previous.id);
  if (state.map.getSource(previous.id)) state.map.removeSource(previous.id);
  delete state.rasters[slot];
}

async function showRaster(slot, name) {
  const request = ++state.requests[slot];
  removeRaster(slot); // Never leave a previous pass/rise visible under a new label.
  issue(slot, null);
  if (!name) { loading(slot, false); return null; }
  loading(slot, true);
  try {
    rasterFile(name);
    const image = await imageFile(name);
    if (request !== state.requests[slot]) return null;
    const id = `${slot}-${request}`;
    state.map.addSource(id, { type: 'image', url: assetURL(name), coordinates: state.coordinates });
    // Observation below scenario; both below vector overlays.
    const before = slot === 'background' && state.rasters.inundation ?
      state.rasters.inundation.id :
      ['corridor-fill', 'corridor-line', 'buildings-fill', 'buildings-points']
        .find(layer => state.map.getLayer(layer));
    state.map.addLayer({
      id, type: 'raster', source: id,
      layout: { visibility: slot === 'inundation' && !el.inundation.checked ? 'none' : 'visible' },
      paint: { 'raster-opacity': slot === 'inundation' ? 0.72 : 0.9,
        'raster-fade-duration': 0,
        'raster-resampling': slot === 'inundation' || name.startsWith('water_mask_') ? 'nearest' : 'linear' },
    }, before);
    state.rasters[slot] = { id, name };
    return image;
  } catch (error) {
    if (request === state.requests[slot]) issue(slot, `Unavailable: ${error.message}`);
    return null;
  } finally {
    if (request === state.requests[slot]) loading(slot, false);
  }
}

function legend() {
  const view = el.view.value;
  el.legend.replaceChildren();
  if (view === 'none') return;
  const description = document.createElement('p');
  if (view === 'water_mask') {
    description.textContent = 'Blue: water observed in the selected radar pass. Dry pixels are transparent.';
    el.legend.append(description);
    return;
  }
  const scale = state.meta.legends?.[view];
  if (!scale || !Number.isFinite(scale.min) || !Number.isFinite(scale.max)) {
    description.textContent = 'Display scale unavailable in metadata.';
    el.legend.append(description);
    return;
  }
  const ramp = document.createElement('div');
  ramp.className = `ramp ${view}`;
  ramp.setAttribute('aria-hidden', 'true');
  const limits = document.createElement('div');
  limits.className = 'range-labels';
  const unit = scale.unit === 'share' ? 'share of passes' : scale.unit;
  for (const value of [scale.min, scale.max]) {
    const label = document.createElement('span');
    label.textContent = `${value} ${unit || ''}`;
    limits.append(label);
  }
  el.legend.append(ramp, limits);
  if (scale.clipped) {
    description.textContent = 'Values outside this display range use the end colours.';
    el.legend.append(description);
  }
}

function renderBackground() {
  const pass = state.meta.passes.find(pass => pass.id === el.pass.value);
  const view = el.view.value;
  el.pass.disabled = !['radar', 'water_mask'].includes(view);
  el['pass-info'].textContent = ['radar', 'water_mask'].includes(view) ?
    `${pass.label} · ${pass.maturity || 'Maturity not supplied'}` : view === 'water_frequency' ?
    'Water frequency combines the exported observation passes.' : view === 'hand' ?
    'HAND measures terrain height above the river in metres.' :
    'Corridor, buildings and inundation can still be shown independently.';
  el['pass-info'].title = pass.scene || '';
  legend();
  const file = view === 'none' ? null : ['radar', 'water_mask'].includes(view) ?
    `${view}_${pass.id}.png` : `${view}.png`;
  void showRaster('background', file);
}

function riseValue() { return state.meta.rise_steps[Number(el.rise.value)]; }

function setBuildingCount() {
  el.count.textContent = '—';
  if (!state.buildings || !state.mask) return;
  const { width, height, alpha } = state.mask;
  const [west, south, east, north] = state.meta.aoi_bbox;
  let flooded = 0;
  for (const feature of state.buildings.features) {
    let inMask = false;
    if (feature.geometry?.type === 'Point') {
      const [lon, lat] = feature.geometry.coordinates;
      const col = Math.floor((lon - west) / (east - west) * width);
      const row = Math.floor((north - lat) / (north - south) * height);
      inMask = col >= 0 && col < width && row >= 0 && row < height && alpha[row * width + col] > 0;
    }
    feature.properties = { ...feature.properties, displayed_inundation: inMask };
    if (inMask) flooded++;
  }
  state.map.getSource('buildings')?.setData(state.buildings);
  el.count.textContent = flooded.toLocaleString();
}

async function renderInundation() {
  const rise = riseValue();
  el['rise-label'].textContent = `${rise.toFixed(1)} m above low-flow level`;
  el.rise.setAttribute('aria-valuetext', `${rise.toFixed(1)} metres above low-flow level`);
  state.mask = null;
  issue('count', null);
  el.count.textContent = '—';
  const file = `inundation/h_${rise.toFixed(1)}.png`;
  const image = await showRaster('inundation', file);
  if (!image || state.rasters.inundation?.name !== file || rise !== riseValue()) return;
  try {
    const canvas = document.createElement('canvas');
    canvas.width = image.naturalWidth;
    canvas.height = image.naturalHeight;
    const context = canvas.getContext('2d', { willReadFrequently: true });
    context.drawImage(image, 0, 0);
    const rgba = context.getImageData(0, 0, canvas.width, canvas.height).data;
    const alpha = new Uint8Array(canvas.width * canvas.height);
    for (let i = 0; i < alpha.length; i++) alpha[i] = rgba[i * 4 + 3];
    state.mask = { width: canvas.width, height: canvas.height, alpha };
    setBuildingCount();
  } catch (error) {
    issue('count', `Building count unavailable: ${error.message}`);
  }
}

function setVectorVisibility(prefix, visible) {
  for (const layer of [`${prefix}-fill`, `${prefix}-line`, `${prefix}-points`]) {
    if (state.map.getLayer(layer)) state.map.setLayoutProperty(layer, 'visibility', visible ? 'visible' : 'none');
  }
}

async function loadCorridor() {
  loading('corridor', true);
  try {
    const data = await jsonFile('corridor.geojson');
    if (data.type !== 'FeatureCollection' || !Array.isArray(data.features)) throw new Error('data/corridor.geojson: invalid FeatureCollection');
    state.map.addSource('corridor', { type: 'geojson', data });
    const before = state.map.getLayer('buildings-fill') ? 'buildings-fill' : undefined;
    state.map.addLayer({ id: 'corridor-fill', type: 'fill', source: 'corridor',
      paint: { 'fill-color': '#cb6e24', 'fill-opacity': 0.07 } }, before);
    state.map.addLayer({ id: 'corridor-line', type: 'line', source: 'corridor',
      paint: { 'line-color': '#a74a09', 'line-width': 2, 'line-dasharray': [3, 1.5] } }, before);
    setVectorVisibility('corridor', el.corridor.checked);
  } catch (error) {
    issue('corridor', `Corridor unavailable: ${error.message}`);
    el.corridor.checked = false;
    el.corridor.disabled = true;
  } finally { loading('corridor', false); }
}

function buildingPopup(event) {
  const properties = event.features[0].properties;
  const card = document.createElement('div');
  const heading = document.createElement('strong');
  heading.textContent = properties.name || properties.id || 'Building';
  card.append(heading);
  const measurement = (value, suffix) => typeof value === 'number' && Number.isFinite(value) ? `${value} ${suffix}` : 'Unknown';
  for (const text of [
    `Height above river: ${measurement(properties.hand_min, 'm')}`,
    `Distance to low-flow channel: ${measurement(properties.dist_m, 'm')}`,
    properties.inside_corridor ? 'Inside the observed river footprint' : 'Outside the observed river footprint',
    state.mask ? `In displayed inundation: ${properties.displayed_inundation ? 'yes' : 'no'}` : 'Inundation sample unavailable',
  ]) {
    const line = document.createElement('p');
    line.textContent = text;
    card.append(line);
  }
  new maplibregl.Popup().setLngLat(event.lngLat).setDOMContent(card).addTo(state.map);
}

async function loadBuildings() {
  loading('buildings', true);
  try {
    const data = await jsonFile('buildings.geojson');
    if (data.type !== 'FeatureCollection' || !Array.isArray(data.features)) throw new Error('data/buildings.geojson: invalid FeatureCollection');
    state.buildings = data;
    state.map.addSource('buildings', { type: 'geojson', data });
    const color = ['match', ['get', 'exposure'], 'inside', '#b84428', 'near', '#d18b28', '#526b65'];
    state.map.addLayer({ id: 'buildings-fill', type: 'fill', source: 'buildings',
      filter: ['==', ['geometry-type'], 'Polygon'], paint: { 'fill-color': color, 'fill-opacity': 0.6 } });
    state.map.addLayer({ id: 'buildings-points', type: 'circle', source: 'buildings',
      filter: ['==', ['geometry-type'], 'Point'], paint: {
        'circle-color': color, 'circle-radius': ['interpolate', ['linear'], ['zoom'], 9, 2, 15, 5],
        'circle-opacity': 0.85,
        'circle-stroke-color': ['case', ['boolean', ['get', 'displayed_inundation'], false], '#101e26', '#ffffff'],
        'circle-stroke-width': ['case', ['boolean', ['get', 'displayed_inundation'], false], 2, 0.6],
      } });
    setVectorVisibility('buildings', el.buildings.checked);
    setBuildingCount();
    if (data.features.some(feature => feature.geometry?.type !== 'Point')) {
      issue('building-count', 'The inundation count includes point features only; other geometries are displayed without sampling.');
    }
    for (const layer of ['buildings-points', 'buildings-fill']) {
      state.map.on('click', layer, buildingPopup);
      state.map.on('mouseenter', layer, () => { state.map.getCanvas().style.cursor = 'pointer'; });
      state.map.on('mouseleave', layer, () => { state.map.getCanvas().style.cursor = ''; });
    }
  } catch (error) {
    issue('buildings', `Buildings unavailable: ${error.message}`);
    el.buildings.checked = false;
    el.buildings.disabled = true;
  } finally { loading('buildings', false); }
}

async function loadValidation() {
  try {
    const data = await jsonFile('validation.json');
    const score = value => Number.isFinite(value) ? value.toFixed(3) : 'not measured';
    el.validation.textContent = `Calibrated on ${data.calibrated_on}: IoU ${score(data.iou_fit)}. ` +
      `Tested on ${data.tested_on}: IoU ${score(data.iou_test)}. Best rise: ` +
      `${Number.isFinite(data.best_rise_m) ? data.best_rise_m + ' m' : 'not supplied'}. ${data.notes || ''}`;
  } catch (error) { el.validation.textContent = `Validation unavailable: ${error.message}`; }
}

function fitArea() {
  const [w, s, e, n] = state.meta.aoi_bbox;
  state.map.fitBounds([[w, s], [e, n]], { padding: 28, duration: 0 });
}

async function initialize() {
  try {
    state.meta = await jsonFile('meta.json');
    checkMetadata(state.meta);
    const [w, s, e, n] = state.meta.aoi_bbox;
    state.coordinates = [[w, n], [e, n], [e, s], [w, s]];
    for (const pass of state.meta.passes) el.pass.add(new Option(pass.label, pass.id));
    const steps = state.meta.rise_steps;
    // The slider indexes metadata levels, including nonuniform future step sets.
    el.rise.max = steps.length - 1;
    el.rise.value = Math.max(0, steps.indexOf(3));
    el['rise-min'].textContent = `${steps[0].toFixed(1)} m`;
    el['rise-max'].textContent = `${steps.at(-1).toFixed(1)} m`;
    for (const credit of state.meta.credits || []) {
      const item = document.createElement('li');
      item.textContent = credit;
      el.credits.append(item);
    }
    el.generated.textContent = state.meta.generated ? `Export generated: ${state.meta.generated}` : '';
    if (typeof maplibregl === 'undefined') throw new Error('Map library unavailable. Check your internet connection and refresh.');
    state.map = new maplibregl.Map({
      container: 'map',
      // Start in the exported Swat River area; image coordinates stay unchanged.
      center: [(w + e) / 2, (s + n) / 2], zoom: 10, bearing: 0, pitch: 0,
      bounds: [[w, s], [e, n]], fitBoundsOptions: { padding: 28 },
      style: {
        version: 8,
        sources: { basemap: { type: 'raster', tileSize: 256,
          // Public cached tiles: no private API key or hosted style is needed.
          tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}'],
          attribution: 'Tiles &copy; <a href="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer">Esri and data contributors</a>; &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>' } },
        layers: [{ id: 'paper', type: 'background', paint: { 'background-color': '#e9ede8' } },
          { id: 'basemap', type: 'raster', source: 'basemap' }],
      },
    });
    state.map.addControl(new maplibregl.NavigationControl(), 'top-right');
    state.map.on('error', event => {
      if (event.sourceId === 'basemap') {
        issue('basemap', 'Basemap unavailable. Exported overlays can still be viewed.');
      } else if (event.sourceId) {
        const slot = Object.keys(state.rasters).find(key => state.rasters[key].id === event.sourceId);
        if (slot) {
          issue(slot, `Unavailable: data/${state.rasters[slot].name}. ${event.error?.message || ''}`);
          removeRaster(slot);
        }
      } else issue('map', `Map error: ${event.error?.message || 'Unable to render the map.'}`);
    });
    state.map.on('style.load', () => {
      el['map-placeholder'].hidden = true;
      el.controls.disabled = false;
      renderBackground();
      void renderInundation();
      void loadCorridor();
      void loadBuildings();
      void loadValidation();
    });
    el.view.addEventListener('change', renderBackground);
    el.pass.addEventListener('change', renderBackground);
    el.rise.addEventListener('input', () => { void renderInundation(); });
    el.corridor.addEventListener('change', () => setVectorVisibility('corridor', el.corridor.checked));
    el.buildings.addEventListener('change', () => setVectorVisibility('buildings', el.buildings.checked));
    el.inundation.addEventListener('change', () => {
      const id = state.rasters.inundation?.id;
      if (id) state.map.setLayoutProperty(id, 'visibility', el.inundation.checked ? 'visible' : 'none');
    });
    el.fit.addEventListener('click', fitArea);
    new ResizeObserver(() => state.map.resize()).observe(document.getElementById('map'));
  } catch (error) {
    el.status.textContent = 'Map unavailable.';
    el['map-placeholder'].textContent = error.message;
    issue('initialization', error.message);
  }
}

void initialize();
