<!-- client/src/views/HomeView.vue -->
<script setup>
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { getStops, getRoutes, getConnections, getVehiclePositions, getRouteStops } from '@/api'

// ── Аккордеон блоков в панели ─────────────────────
const openBlocks = ref({
  transport: true,   // «Данные транспорта» открыт по умолчанию
  ranking:   false,
  analysis:  false,
})

function toggleBlock(key) {
  openBlocks.value[key] = !openBlocks.value[key]
}

// Элементы инфраструктуры для рендера в панели
const infraItems =[
  { key: 'stops',    label: 'Остановки',       color: '#198754' },
  { key: 'vehicles', label: 'История позиций', color: '#0d6efd' }
]

// ── Карта ─────────────────────────────────────────
let map = null
let drawnItems = null // Группа слоев для нарисованных полигонов
const activePolygon = ref(null) // Хранит GeoJSON нарисованной области

const infraCache    = {}
const routeCache    = {}
const rankCache     = {}
const analysisCache = {}
const IRKUTSK       =[52.286387, 104.289567]

const PALETTE =[
  '#e63946','#2a9d8f','#e9c46a','#f4a261','#457b9d',
  '#6a4c93','#2dc653','#ff595e','#48cae4','#bc4749',
  '#e76f51','#1982c4','#8ac926','#ffca3a','#6a994e',
]
let ci = 0
const nextColor = () => PALETTE[ci++ % PALETTE.length]

// ── Состояние слоёв ───────────────────────────────
const infraEnabled  = ref({ stops: false, vehicles: false })
const infraLoading  = ref({ stops: false, vehicles: false })
const infraCounts   = ref({ stops: '—', vehicles: '—' })

const routeItems    = ref([])
const routesReady   = ref(false)
const routesLoading = ref(false)
const openGroups    = ref({})

const routesByType = computed(() => {
  const g = {}
  routeItems.value.forEach(r => {
    const t = r.transport_type?.name || 'Прочие'
    ;(g[t] = g[t] ||[]).push(r)
  })
  return g
})

// Слои Районирование
const rankLayers = ref({
  routeRank:    { label: 'Рейтинг маршрутов',  active: false, loading: false, disabled: true,  desc: 'Доступно после интеграции с модулем анализа' },
  stopsDensity: { label: 'Плотность остановок', active: false, loading: false, disabled: false, desc: 'Концентрация остановок по районам' },
})

// Слои анализа доступности
const analysisLayers = ref({
  heatmap:   { label: 'Зоны доступности (400м)', active: false, loading: false, disabled: false, desc: 'Охват населения пешей доступностью от остановок' },
  intervals: { label: 'Интервалы движения',       active: false, loading: false, disabled: true,  desc: 'Доступно после интеграции с модулем анализа' },
})

const status       = ref('Готов')
const cursorCoords = ref('Наведите курсор на карту')
const activeCount  = ref(0)

// ── Инициализация ─────────────────────────────────
onMounted(async () => {
  await initLeaflet()
  localizeLeafletDraw() // Русификация инструментов рисования
  initMap()
  fetchRouteList()
})
onUnmounted(() => { if (map) { map.remove(); map = null } })

function initLeaflet() {
  return new Promise(resolve => {
    if (window.L && window.L.Control.Draw && window.turf) { resolve(); return }

    // Подгрузка CSS (Leaflet + Draw)
    const cssL = document.createElement('link'); cssL.rel = 'stylesheet'; cssL.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'; document.head.appendChild(cssL);
    const cssD = document.createElement('link'); cssD.rel = 'stylesheet'; cssD.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.css'; document.head.appendChild(cssD);

    // Подгрузка JS (Leaflet -> Draw -> Turf.js)
    const jsL = document.createElement('script'); jsL.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    jsL.onload = () => {
      const jsD = document.createElement('script'); jsD.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.js';
      jsD.onload = () => {
        const jsT = document.createElement('script'); jsT.src = 'https://cdn.jsdelivr.net/npm/@turf/turf@6/turf.min.js';
        jsT.onload = resolve;
        document.head.appendChild(jsT);
      };
      document.head.appendChild(jsD);
    };
    document.head.appendChild(jsL);
  })
}

// Русификация интерфейса Leaflet.Draw
function localizeLeafletDraw() {
  const L = window.L;
  if (!L || !L.drawLocal) return;

  // Тексты панели рисования
  L.drawLocal.draw.toolbar.actions.title = 'Отменить рисование';
  L.drawLocal.draw.toolbar.actions.text = 'Отмена';
  L.drawLocal.draw.toolbar.finish.title = 'Завершить рисование';
  L.drawLocal.draw.toolbar.finish.text = 'Завершить';
  L.drawLocal.draw.toolbar.undo.title = 'Удалить последнюю точку';
  L.drawLocal.draw.toolbar.undo.text = 'Удалить точку';
  L.drawLocal.draw.toolbar.buttons.polygon = 'Нарисовать полигон (область)';

  // Подсказки при рисовании полигона
  L.drawLocal.draw.handlers.polygon.tooltip.start = 'Кликните, чтобы начать рисование области.';
  L.drawLocal.draw.handlers.polygon.tooltip.cont = 'Кликните, чтобы добавить точку.';
  L.drawLocal.draw.handlers.polygon.tooltip.end = 'Кликните на первую точку, чтобы замкнуть полигон.';

  // Тексты панели редактирования
  L.drawLocal.edit.toolbar.actions.save.title = 'Сохранить изменения';
  L.drawLocal.edit.toolbar.actions.save.text = 'Сохранить';
  L.drawLocal.edit.toolbar.actions.cancel.title = 'Отменить редактирование, отбросить все изменения';
  L.drawLocal.edit.toolbar.actions.cancel.text = 'Отмена';
  L.drawLocal.edit.toolbar.actions.clearAll.title = 'Очистить все выделения';
  L.drawLocal.edit.toolbar.actions.clearAll.text = 'Удалить всё';
  L.drawLocal.edit.toolbar.buttons.edit = 'Редактировать выделенную область';
  L.drawLocal.edit.toolbar.buttons.editDisabled = 'Нет областей для редактирования';
  L.drawLocal.edit.toolbar.buttons.remove = 'Удалить выделенную область';
  L.drawLocal.edit.toolbar.buttons.removeDisabled = 'Нет областей для удаления';

  // Подсказки при редактировании/удалении
  L.drawLocal.edit.handlers.edit.tooltip.text = 'Перетаскивайте узлы, чтобы изменить область.';
  L.drawLocal.edit.handlers.edit.tooltip.subtext = 'Нажмите "Отмена", чтобы отменить изменения.';
  L.drawLocal.edit.handlers.remove.tooltip.text = 'Кликните по области, чтобы удалить её.';
}

function initMap() {
  map = window.L.map('leaflet-map', { center: IRKUTSK, zoom: 12 })
  window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap', maxZoom: 19,
  }).addTo(map)
  
  map.on('mousemove', e => {
    cursorCoords.value = `${e.latlng.lat.toFixed(5)}, ${e.latlng.lng.toFixed(5)}`
  })

  // Инициализация инструментов рисования
  drawnItems = new window.L.FeatureGroup();
  map.addLayer(drawnItems);

  const drawControl = new window.L.Control.Draw({
    edit: { featureGroup: drawnItems },
    draw: {
      polyline: false,
      circle: false,
      circlemarker: false,
      marker: false,
      rectangle: false, // Отключили прямоугольник
      polygon: {
        allowIntersection: false, // Запретить пересечение линий полигона
        drawError: {
          color: '#e1e100', // Цвет ошибки при пересечении
          message: '<strong>Ошибка:</strong> линии не могут пересекаться!' // Сообщение об ошибке
        },
        shapeOptions: {
          color: '#0d6efd'
        }
      }
    }
  });
  map.addControl(drawControl);

  // События рисования
  map.on(window.L.Draw.Event.CREATED, function (e) {
    drawnItems.clearLayers(); // Оставляем только один полигон за раз
    drawnItems.addLayer(e.layer);
    activePolygon.value = e.layer.toGeoJSON();
    refreshMapByPolygon();
  });

  map.on(window.L.Draw.Event.EDITED, function (e) {
    const layers = drawnItems.getLayers();
    if (layers.length > 0) activePolygon.value = layers[0].toGeoJSON();
    refreshMapByPolygon();
  });

  map.on(window.L.Draw.Event.DELETED, function (e) {
    if (drawnItems.getLayers().length === 0) activePolygon.value = null;
    refreshMapByPolygon();
  });
}

// Очистка полигона по кнопке
function clearPolygon() {
  if (drawnItems) drawnItems.clearLayers();
  activePolygon.value = null;
  refreshMapByPolygon();
}

// Перерисовка слоев при изменении полигона
async function refreshMapByPolygon() {
  const wasStops = infraEnabled.value.stops;
  const wasVehicles = infraEnabled.value.vehicles;
  const activeRoutes = routeItems.value.filter(r => r.enabled);

  // 1. Выключаем активные слои
  if (wasStops) await toggleInfra('stops', false);
  if (wasVehicles) await toggleInfra('vehicles', false);
  for (const r of activeRoutes) await toggleRoute(r, false);

  // 2. Очищаем кеш, чтобы они заново отрендерились с учетом полигона
  delete infraCache['stops'];
  delete infraCache['vehicles'];
  activeRoutes.forEach(r => { delete routeCache[r.name] });

  // 3. Включаем обратно
  if (wasStops) await toggleInfra('stops', true);
  if (wasVehicles) await toggleInfra('vehicles', true);
  for (const r of activeRoutes) await toggleRoute(r, true);
}


// ── Маршруты ──────────────
async function fetchRouteList() {
  routesLoading.value = true
  try {
    const { data } = await getRoutes()
    const byName = {}
    data.forEach(r => {
      const name = r.name?.trim() || `Маршрут ${r.id}`
      if (!byName[name]) {
        byName[name] = {
          name, ids:[], transport_type: r.transport_type,
          color: nextColor(), enabled: false, loading: false, tripCount: null,
        }
      }
      byName[name].ids.push(r.id)
    })
    routeItems.value = Object.values(byName).sort((a, b) => a.name.localeCompare(b.name, 'ru'))
    routesReady.value = true
  } catch (_) {
    status.value = 'Ошибка загрузки маршрутов'
  }
  routesLoading.value = false
}

function haversine([lat1, lon1], [lat2, lon2]) {
  const R    = 6371000
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a    = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function thin(pts, d = 40) {
  if (!pts.length) return []
  const out = [pts[0]]
  for (let i = 1; i < pts.length; i++) {
    if (haversine(out[out.length - 1], pts[i]) >= d) out.push(pts[i])
  }
  return out
}

function snapToStops(coords, stopCoords, maxD = 80) {
  if (!stopCoords.length) return coords
  return coords.map(pt => {
    let best = null, bestD = Infinity
    stopCoords.forEach(s => { const d = haversine(pt, s); if (d < bestD) { bestD = d; best = s } })
    return bestD <= maxD ? best : pt
  })
}

async function buildRouteLayer(route) {
  const L = window.L
  const [posResults, rsResult] = await Promise.all([
    Promise.all(route.ids.map(id => getVehiclePositions(null, id).catch(() => ({ data: [] })))),
    getRouteStops().catch(() => ({ data:[] })),
  ])
  const allPos = posResults
    .flatMap(r => Array.isArray(r.data) ? r.data : (r.data?.results ||[]))
    .filter(p => p.latitude && p.longitude)

  const stopCoords = (rsResult.data ||[])
    .filter(rs => route.ids.includes(rs.route?.id) && rs.stop?.latitude)
    .sort((a, b) => a.order - b.order)
    .map(rs =>[rs.stop.latitude, rs.stop.longitude])

  const grp = L.layerGroup()
  if (!allPos.length) return { grp, tripCount: 0 }

  const byVehicle = {}
  allPos.forEach(p => {
    const key = p.vehicle?.gos_num || p.vehicle?.id || 'unknown'
    ;(byVehicle[key] = byVehicle[key] ||[]).push(p)
  })

  // Сборка треков
  let tracks = Object.values(byVehicle).map(pts => {
    pts.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    return { count: pts.length, coords: snapToStops(thin(pts.map(p => [p.latitude, p.longitude]), 40), stopCoords) }
  }).filter(t => t.coords.length >= 2)

  // ФИЛЬТРАЦИЯ ТРЕКОВ ПО ПОЛИГОНУ (Turf.js)
  if (activePolygon.value) {
    tracks = tracks.filter(t => {
      const lineCoords = t.coords.map(c => [c[1], c[0]]); // Leaflet[lat, lng] -> Turf [lng, lat]
      const line = window.turf.lineString(lineCoords);
      return window.turf.booleanIntersects(line, activePolygon.value);
    });
  }

  if (!tracks.length) return { grp, tripCount: 0 }
  tracks.sort((a, b) => b.count - a.count)

  tracks.slice(1).forEach(t =>
    L.polyline(t.coords, { color: route.color, weight: 1.5, opacity: 0.25 }).addTo(grp)
  )
  L.polyline(tracks[0].coords, { color: route.color, weight: 4, opacity: 0.9 })
    .bindPopup(`<b>${route.name}</b><br><small class="text-muted">ТС: ${tracks.length}</small>`)
    .addTo(grp)

  // Фильтруем остановки для отображения, если есть полигон
  stopCoords.forEach((coord, i) => {
    if (activePolygon.value) {
      const pt = window.turf.point([coord[1], coord[0]]);
      if (!window.turf.booleanPointInPolygon(pt, activePolygon.value)) return;
    }
    L.circleMarker(coord, {
      radius: 5, color: route.color, fillColor: '#fff', fillOpacity: 1, weight: 2.5,
    }).bindTooltip(`${route.name} — ост. ${i + 1}`, { direction: 'top' }).addTo(grp)
  })

  return { grp, tripCount: tracks.length }
}

async function toggleRoute(route, enabled) {
  if (enabled) {
    if (!routeCache[route.name]) {
      route.loading = true
      status.value = `Загрузка: ${route.name}...`
      try {
        const { grp, tripCount } = await buildRouteLayer(route)
        routeCache[route.name] = grp
        route.tripCount = tripCount
        status.value = 'Готов'
      } catch (_) {
        status.value = 'Ошибка'; route.loading = false; route.enabled = false; return
      }
      route.loading = false
    }
    routeCache[route.name].addTo(map)
    route.enabled = true; activeCount.value++
  } else {
    if (routeCache[route.name] && map.hasLayer(routeCache[route.name])) {
      map.removeLayer(routeCache[route.name])
    }
    route.enabled = false; activeCount.value = Math.max(0, activeCount.value - 1)
  }
}

// ── Инфраструктурные слои ─────────────────────────
function dotIcon(color) {
  return window.L.divIcon({
    className: '',
    html: `<svg width="14" height="14"><circle cx="7" cy="7" r="5.5" fill="${color}" stroke="white" stroke-width="1.5"/></svg>`,
    iconSize: [14, 14], iconAnchor:[7, 7],
  })
}

async function loadStops() {
  const { data } = await getStops()
  const grp = window.L.layerGroup()
  let count = 0;
  
  data.forEach(s => {
    if (!s.latitude || !s.longitude) return
    
    // ФИЛЬТРАЦИЯ ПО ПОЛИГОНУ
    if (activePolygon.value) {
      const pt = window.turf.point([s.longitude, s.latitude]);
      if (!window.turf.booleanPointInPolygon(pt, activePolygon.value)) return;
    }

    window.L.marker([s.latitude, s.longitude], { icon: dotIcon('#198754') })
      .bindPopup(`<b>${s.name}</b><br><small class="text-muted">${s.latitude.toFixed(5)}, ${s.longitude.toFixed(5)}</small>`)
      .bindTooltip(s.name, { direction: 'top' })
      .addTo(grp)
    count++;
  })
  infraCounts.value.stops = count
  return grp
}

async function loadVehicles() {
  const { data } = await getVehiclePositions()
  const grp = window.L.layerGroup()
  const list = Array.isArray(data) ? data : (data?.results ||[])
  let count = 0;

  list.forEach(p => {
    if (!p.latitude || !p.longitude) return

    // ФИЛЬТРАЦИЯ ПО ПОЛИГОНУ
    if (activePolygon.value) {
      const pt = window.turf.point([p.longitude, p.latitude]);
      if (!window.turf.booleanPointInPolygon(pt, activePolygon.value)) return;
    }

    window.L.marker([p.latitude, p.longitude], { icon: dotIcon('#0d6efd') })
      .bindPopup(`<b>${p.vehicle?.gos_num || '—'}</b><br>
        Маршрут: ${p.route?.name || '—'}<br>
        Скорость: ${p.speed} км/ч<br>
        <small class="text-muted">${new Date(p.timestamp).toLocaleString('ru-RU')}</small>`)
      .addTo(grp)
    count++;
  })
  infraCounts.value.vehicles = count
  return grp
}

const infraLoaders = { stops: loadStops, vehicles: loadVehicles }

async function toggleInfra(name, enabled) {
  if (enabled) {
    if (!infraCache[name]) {
      infraLoading.value[name] = true; status.value = 'Загрузка...'
      try {
        infraCache[name] = await infraLoaders[name]()
        status.value = 'Готов'
      } catch (_) {
        status.value = 'Ошибка'; infraLoading.value[name] = false; infraEnabled.value[name] = false; return
      }
      infraLoading.value[name] = false
    }
    infraCache[name].addTo(map); infraEnabled.value[name] = true; activeCount.value++
  } else {
    if (infraCache[name] && map.hasLayer(infraCache[name])) map.removeLayer(infraCache[name])
    infraEnabled.value[name] = false; activeCount.value = Math.max(0, activeCount.value - 1)
  }
}

// ── Слои Районирование и доступности ─────────────────────────────
async function toggleRankLayer(key) {
  const layer = rankLayers.value[key]; if (layer.disabled) return
  const enabled = !layer.active
  if (enabled) {
    if (!rankCache[key]) {
      layer.loading = true; status.value = 'Загрузка...';
      try {
        const grp = window.L.layerGroup();
        if (key === 'stopsDensity') {
          const { data: stops } = await getStops()
          const withCoords = stops.filter(s => s.latitude && s.longitude)
          withCoords.forEach(s => {
            if (activePolygon.value && !window.turf.booleanPointInPolygon(window.turf.point([s.longitude, s.latitude]), activePolygon.value)) return;
            const neighbors = withCoords.filter(o => o.id !== s.id && haversine([s.latitude, s.longitude],[o.latitude, o.longitude]) < 400).length
            const intensity = Math.min(neighbors / 10, 1)
            const color = `hsl(${Math.round((1 - intensity) * 120)}, 80%, 42%)`
            window.L.circleMarker([s.latitude, s.longitude], { radius: 5 + neighbors * 1.2, color, fillColor: color, fillOpacity: 0.5, weight: 1 })
              .bindTooltip(`${s.name} — соседей в 400м: ${neighbors}`, { direction: 'top' }).addTo(grp)
          })
        }
        rankCache[key] = grp; status.value = 'Готов'
      } catch (_) { status.value = 'Ошибка'; layer.loading = false; return }
      layer.loading = false
    }
    rankCache[key].addTo(map); layer.active = true; activeCount.value++
  } else {
    if (rankCache[key] && map.hasLayer(rankCache[key])) map.removeLayer(rankCache[key])
    layer.active = false; activeCount.value = Math.max(0, activeCount.value - 1)
  }
}

async function toggleAnalysisLayer(key) {
  const layer = analysisLayers.value[key]; if (layer.disabled) return
  const enabled = !layer.active
  if (enabled) {
    if (!analysisCache[key]) {
      layer.loading = true; status.value = 'Загрузка...'
      try {
        const grp = window.L.layerGroup()
        if (key === 'heatmap') {
          const { data: stops } = await getStops()
          stops.filter(s => s.latitude && s.longitude).forEach(s => {
            if (activePolygon.value && !window.turf.booleanPointInPolygon(window.turf.point([s.longitude, s.latitude]), activePolygon.value)) return;
            window.L.circle([s.latitude, s.longitude], { radius: 400, color: '#0d6efd', fillColor: '#0d6efd', fillOpacity: 0.07, weight: 0 }).addTo(grp)
            window.L.circle([s.latitude, s.longitude], { radius: 200, color: '#0d6efd', fillColor: '#0d6efd', fillOpacity: 0.12, weight: 0 }).addTo(grp)
          })
        }
        analysisCache[key] = grp; status.value = 'Готов'
      } catch (_) { status.value = 'Ошибка'; layer.loading = false; return }
      layer.loading = false
    }
    analysisCache[key].addTo(map); layer.active = true; activeCount.value++
  } else {
    if (analysisCache[key] && map.hasLayer(analysisCache[key])) map.removeLayer(analysisCache[key])
    layer.active = false; activeCount.value = Math.max(0, activeCount.value - 1)
  }
}

function fitToVisible() {
  const all =[...Object.values(infraCache), ...Object.values(routeCache), ...Object.values(rankCache), ...Object.values(analysisCache)]
    .filter(l => l && map.hasLayer(l)).map(l => { try { return l.getBounds() } catch (_) { return null } }).filter(b => b?.isValid())
  if (!all.length) { map.setView(IRKUTSK, 12); return }
  map.fitBounds(all.reduce((a, b) => a.extend(b)), { padding: [30, 30] })
}
</script>

<template>
  <div class="d-flex h-100">

    <!-- ══ ЛЕВАЯ ПАНЕЛЬ ═══════════════════════════════ -->
    <aside class="left-panel">

      <!-- ── БЛОК 1: Данные транспорта ─────────────── -->
      <div class="acc-block" :class="{ open: openBlocks.transport }">
        <div class="acc-header" @click="toggleBlock('transport')">
          <span class="acc-title">Данные транспорта</span>
          <span class="acc-arrow">{{ openBlocks.transport ? '−' : '+' }}</span>
        </div>
        <div class="acc-body">
          
          <div v-if="activePolygon" class="alert alert-warning m-2 py-1 px-2" style="font-size:11px;">
            Включен фильтр по зоне. Нажмите кнопку внизу, чтобы очистить.
          </div>

          <div class="acc-section-label">Показать на карте</div>

          <label v-for="item in infraItems" :key="item.key"
                 class="layer-row" :class="{ 'row-active': infraEnabled[item.key] }">
            <input type="checkbox"
                   class="form-check-input mt-0 flex-shrink-0"
                   :checked="infraEnabled[item.key]"
                   :disabled="infraLoading[item.key]"
                   @change="e => toggleInfra(item.key, e.target.checked)"/>
            <span class="l-dot rounded-circle flex-shrink-0" :style="`background:${item.color}`"></span>
            <span class="l-label">{{ item.label }}</span>
            <span class="l-count">{{ infraCounts[item.key] }}</span>
            <span v-if="infraLoading[item.key]" class="mini-spin"></span>
          </label>

          <div class="acc-section-label mt-2">Маршруты<span v-if="routesLoading" class="mini-spin ms-1"></span></div>

          <template v-if="routesReady">
            <div v-for="(routes, type) in routesByType" :key="type">
              <div class="route-group-hdr" @click="openGroups[type] = !openGroups[type]">
                <span class="flex-grow-1" style="font-size:12px; font-weight:600; color:#343a40;">{{ type }}</span>
                <span class="l-count">{{ routes.length }}</span>
                <span style="font-size:13px; color:#adb5bd; width:14px; text-align:center; margin-left:4px;">{{ openGroups[type] ? '−' : '+' }}</span>
              </div>
              <div v-show="openGroups[type]">
                <label v-for="route in routes" :key="route.name" class="layer-row ps-route" :class="{ 'row-active': route.enabled }">
                  <input type="checkbox" class="form-check-input mt-0 flex-shrink-0" :checked="route.enabled" :disabled="route.loading" @change="e => toggleRoute(route, e.target.checked)"/>
                  <span class="l-line flex-shrink-0" :style="`background:${route.color}`"></span>
                  <span class="l-label text-truncate" :title="route.name">{{ route.name }}</span>
                  <span v-if="route.tripCount !== null" class="l-count">{{ route.tripCount }} ТС</span>
                  <span v-if="route.loading" class="mini-spin"></span>
                </label>
              </div>
            </div>
          </template>

        </div>
      </div>

      <!-- ── БЛОК 2: Районирование ───────────────────── -->
      <div class="acc-block" :class="{ open: openBlocks.ranking }">
        <div class="acc-header" @click="toggleBlock('ranking')">
          <span class="acc-title">Районирование</span>
          <span class="acc-arrow">{{ openBlocks.ranking ? '−' : '+' }}</span>
        </div>
        <div class="acc-body">
          <div v-for="(layer, key) in rankLayers" :key="key" class="layer-action-row" :class="{ 'is-disabled': layer.disabled, 'is-active': layer.active }">
            <div class="lar-info">
              <div class="lar-label">{{ layer.label }}</div>
              <div v-if="layer.disabled" class="lar-desc">{{ layer.desc }}</div>
            </div>
            <button v-if="!layer.disabled" class="lar-btn" :disabled="layer.loading" @click="toggleRankLayer(key)">
              <span v-if="layer.loading" class="mini-spin"></span>
              <span v-else>{{ layer.active ? 'Скрыть' : 'Показать' }}</span>
            </button>
            <span v-else class="lar-soon">скоро</span>
          </div>
        </div>
      </div>

      <!-- ── БЛОК 3: Анализ доступности ────────────── -->
      <div class="acc-block" :class="{ open: openBlocks.analysis }">
        <div class="acc-header" @click="toggleBlock('analysis')">
          <span class="acc-title">Анализ доступности</span>
          <span class="acc-arrow">{{ openBlocks.analysis ? '−' : '+' }}</span>
        </div>
        <div class="acc-body">
          <div v-for="(layer, key) in analysisLayers" :key="key" class="layer-action-row" :class="{ 'is-disabled': layer.disabled, 'is-active': layer.active }">
            <div class="lar-info">
              <div class="lar-label">{{ layer.label }}</div>
              <div v-if="layer.disabled" class="lar-desc">{{ layer.desc }}</div>
            </div>
            <button v-if="!layer.disabled" class="lar-btn" :disabled="layer.loading" @click="toggleAnalysisLayer(key)">
              <span v-if="layer.loading" class="mini-spin"></span>
              <span v-else>{{ layer.active ? 'Скрыть' : 'Показать' }}</span>
            </button>
            <span v-else class="lar-soon">скоро</span>
          </div>
        </div>
      </div>

      <!-- Кнопки карты — всегда видны внизу -->
      <div class="panel-footer flex-column" style="gap:5px;">
        <div class="d-flex" style="gap:8px;">
            <button class="btn btn-sm btn-outline-secondary flex-fill" title="Вписать слои" @click="fitToVisible">Вписать слои</button>
            <button class="btn btn-sm btn-outline-secondary flex-fill" title="Центр города" @click="map.setView(IRKUTSK, 12)">Центр города</button>
        </div>
        <!-- Кнопка сброса зоны, видна только если нарисован полигон -->
        <button v-if="activePolygon" class="btn btn-sm btn-danger w-100" @click="clearPolygon">
          Очистить выделенную зону
        </button>
      </div>

      <!-- Статус -->
      <div class="panel-status">
        <span>Слоёв: {{ activeCount }}</span>
        <span class="mx-2 text-muted">|</span>
        <span class="text-truncate">{{ status }}</span>
      </div>

    </aside>

    
    <!-- ══ КАРТА ════════════════════════════════════ -->
    <div class="map-wrap">
      <div id="leaflet-map"></div>
      <div class="map-coords">{{ cursorCoords }}</div>
    </div>
  </div>
</template>

<style scoped>
/* ── Root ─────────────────────────────────────────── */
.d-flex.h-100 { height: 100%; overflow: hidden; }

/* ── Левая панель ─────────────────────────────────── */
.left-panel {
  width: 268px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #dee2e6;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Аккордеон ────────────────────────────────────── */
.acc-block { border-bottom: 1px solid #dee2e6; flex-shrink: 0; }
.acc-header { display: flex; align-items: center; justify-content: space-between; padding: 11px 14px; cursor: pointer; user-select: none; background: #f8f9fa; transition: background .12s; }
.acc-header:hover { background: #eef0f2; }
.acc-title { font-size: 13px; font-weight: 600; color: #212529; }
.acc-arrow { font-size: 16px; color: #adb5bd; line-height: 1; width: 16px; text-align: center; }
.acc-body { display: none; padding: 8px 0; overflow-y: auto; max-height: 420px; scrollbar-width: thin; scrollbar-color: #dee2e6 transparent; }
.acc-block.open { flex-shrink: 1; overflow: hidden; display: flex; flex-direction: column; }
.acc-block.open .acc-body { display: block; }

.acc-section-label { font-size: 10px; font-weight: 700; color: #adb5bd; text-transform: uppercase; letter-spacing: .6px; padding: 4px 14px 5px; display: flex; align-items: center; }

/* ── Строки чекбоксов ─────────────────────────────── */
.layer-row { display: flex; align-items: center; gap: 8px; padding: 6px 14px; cursor: pointer; transition: background .12s; border-left: 2px solid transparent; }
.layer-row:hover { background: #f8f9fa; }
.layer-row.row-active { background: #f0f4ff; border-left-color: #0d6efd; }
.ps-route { padding-left: 26px !important; }

.l-dot  { width: 9px; height: 9px; }
.l-line { width: 18px; height: 3px; border-radius: 2px; }
.l-label { flex: 1; font-size: 12.5px; color: #212529; min-width: 0; }
.l-count { font-size: 10px; color: #adb5bd; white-space: nowrap; flex-shrink: 0; }

.route-group-hdr { display: flex; align-items: center; padding: 5px 14px; cursor: pointer; transition: background .12s; user-select: none; }
.route-group-hdr:hover { background: #f8f9fa; }

/* ── Карточки действий ─────── */
.layer-action-row { display: flex; align-items: center; gap: 10px; padding: 9px 14px; border-left: 2px solid transparent; transition: background .12s; }
.layer-action-row:not(.is-disabled):hover { background: #f8f9fa; }
.layer-action-row.is-active { background: #f0f4ff; border-left-color: #0d6efd; }
.layer-action-row.is-disabled { opacity: .55; }
.lar-info { flex: 1; min-width: 0; }
.lar-label { font-size: 13px; font-weight: 500; color: #212529; }
.lar-desc  { font-size: 11px; color: #6c757d; margin-top: 2px; line-height: 1.3; }
.lar-btn { flex-shrink: 0; padding: 4px 10px; font-size: 12px; border: 1px solid #dee2e6; border-radius: 6px; background: #fff; cursor: pointer; font-family: inherit; transition: all .15s; white-space: nowrap; }
.lar-btn:hover:not(:disabled) { background: #0d6efd; color: #fff; border-color: #0d6efd; }
.layer-action-row.is-active .lar-btn { background: #0d6efd; color: #fff; border-color: #0d6efd; }
.lar-btn:disabled { opacity: .6; cursor: wait; }
.lar-soon { flex-shrink: 0; font-size: 10px; color: #adb5bd; background: #f0f0f0; border-radius: 10px; padding: 2px 8px; white-space: nowrap; }

/* ── Футер и статус панели ────────────────────────── */
.panel-footer { display: flex; padding: 10px 12px; border-top: 1px solid #dee2e6; flex-shrink: 0; margin-top: auto; }
.panel-status { display: flex; align-items: center; padding: 4px 14px; font-size: 11px; color: #6c757d; background: #f8f9fa; border-top: 1px solid #dee2e6; flex-shrink: 0; }

/* ── Карта ────────────────────────────────────────── */
.map-wrap { position: relative; flex: 1; overflow: hidden; z-index: 1; }
#leaflet-map { width: 100%; height: 100%; }

.map-coords {
  position: absolute; bottom: 0; left: 0; right: 0; height: 24px; background: rgba(255,255,255,.88); border-top: 1px solid #dee2e6; display: flex; align-items: center; padding: 0 10px; font-size: 11px; color: #6c757d; z-index: 1000;
}

/* ── Спиннер ──────────────────────────────────────── */
.mini-spin { display: inline-block; width: 12px; height: 12px; border: 2px solid #dee2e6; border-top-color: #0d6efd; border-radius: 50%; animation: spin .8s linear infinite; flex-shrink: 0; }
@keyframes spin { to { transform: rotate(360deg); } }
.mt-2 { margin-top: 8px !important; }
.ms-1 { margin-left: 4px !important; }
</style>