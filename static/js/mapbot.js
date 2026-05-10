/**
 * Traveloop — Floating Map Bot
 *
 * A floating map widget that:
 * 1. Shows all geocoded destinations on a mini-map
 * 2. Lets you search/filter cities in a list
 * 3. Auto-detects clicks on any element with [data-city-name]
 *    and flies the map to that city
 * 4. Scans the page for city names and makes them interactive
 */

(function () {
  'use strict';

  let mapInstance = null;
  let citiesData = [];
  let markers = {};
  let panelOpen = false;
  let leafletLoaded = false;

  // ─── DOM References ───
  const toggle = document.getElementById('mapbotToggle');
  const panel = document.getElementById('mapbotPanel');
  const mapContainer = document.getElementById('mapbotMap');
  const searchInput = document.getElementById('mapbotSearch');
  const cityList = document.getElementById('mapbotCityList');
  const headerCity = document.getElementById('mapbotHeaderCity');

  if (!toggle || !panel) return;

  // ─── Load Leaflet dynamically ───
  function loadLeaflet(callback) {
    if (leafletLoaded) { callback(); return; }
    const css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    document.head.appendChild(css);

    const js = document.createElement('script');
    js.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    js.onload = () => { leafletLoaded = true; callback(); };
    document.head.appendChild(js);
  }

  // ─── Fetch Cities ───
  function fetchCities() {
    fetch('/destinations/api/cities/')
      .then(r => r.json())
      .then(data => {
        citiesData = data;
        renderCityList(data);
        if (mapInstance) addMarkers(data);
        scanPageForCities();
      })
      .catch(() => {});
  }

  // ─── Render City List ───
  function renderCityList(cities) {
    if (!cityList) return;
    cityList.innerHTML = '';
    cities.forEach(city => {
      const item = document.createElement('div');
      item.className = 'mapbot-city-item';
      item.dataset.cityId = city.id;
      item.innerHTML = `
        <span class="mapbot-city-dot"></span>
        <span class="mapbot-city-name">${city.name}</span>
        <span class="mapbot-city-country">${city.country}</span>
      `;
      item.addEventListener('click', () => flyToCity(city));
      cityList.appendChild(item);
    });
  }

  // ─── Init Map ───
  function initMap() {
    if (mapInstance || !mapContainer) return;
    mapInstance = L.map('mapbotMap', {
      scrollWheelZoom: true,
      zoomControl: false,
    }).setView([20, 0], 2);

    L.control.zoom({ position: 'topright' }).addTo(mapInstance);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OSM',
      maxZoom: 18,
    }).addTo(mapInstance);

    addMarkers(citiesData);
    setTimeout(() => mapInstance.invalidateSize(), 300);
  }

  // ─── Add Markers ───
  function addMarkers(cities) {
    if (!mapInstance) return;
    const markerIcon = L.divIcon({
      className: 'custom-map-marker',
      html: '<svg width="24" height="32" viewBox="0 0 28 36"><path d="M14 0C6.27 0 0 6.27 0 14c0 10.5 14 22 14 22s14-11.5 14-22C28 6.27 21.73 0 14 0z" fill="#e8734a" stroke="#fff" stroke-width="2"/><circle cx="14" cy="13" r="5" fill="#fff"/></svg>',
      iconSize: [24, 32],
      iconAnchor: [12, 32],
      popupAnchor: [0, -30],
    });

    cities.forEach(city => {
      if (!city.latitude || !city.longitude) return;
      const marker = L.marker([city.latitude, city.longitude], { icon: markerIcon }).addTo(mapInstance);
      marker.bindPopup(`
        <div style="font-family:'Caveat',cursive;font-size:1.2rem;font-weight:700;">${city.name}</div>
        <div style="font-size:0.8rem;color:#666;">${city.country}${city.region ? ' · ' + city.region : ''}</div>
        ${city.description ? '<div style="font-size:0.78rem;margin-top:4px;color:#888;">' + city.description + '</div>' : ''}
      `);
      markers[city.name.toLowerCase()] = { marker, city };
    });
  }

  // ─── Fly to City ───
  function flyToCity(city) {
    if (!mapInstance) return;

    // Open panel if not already
    if (!panelOpen) togglePanel();

    mapInstance.flyTo([city.latitude, city.longitude], 10, {
      duration: 1.2,
    });

    // Open popup
    const key = city.name.toLowerCase();
    if (markers[key]) {
      setTimeout(() => markers[key].marker.openPopup(), 800);
    }

    // Highlight in list
    document.querySelectorAll('.mapbot-city-item').forEach(el => {
      el.classList.toggle('active', parseInt(el.dataset.cityId) === city.id);
    });

    // Update header
    if (headerCity) {
      headerCity.textContent = `📍 ${city.name}, ${city.country}`;
    }
  }

  // ─── Toggle Panel ───
  function togglePanel() {
    panelOpen = !panelOpen;
    panel.classList.toggle('open', panelOpen);
    toggle.classList.toggle('active', panelOpen);

    if (panelOpen && !mapInstance) {
      loadLeaflet(() => {
        initMap();
        setTimeout(() => mapInstance && mapInstance.invalidateSize(), 400);
      });
    } else if (panelOpen && mapInstance) {
      setTimeout(() => mapInstance.invalidateSize(), 200);
    }
  }

  // ─── Search Filter ───
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.toLowerCase().trim();
      const filtered = citiesData.filter(c =>
        c.name.toLowerCase().includes(q) ||
        c.country.toLowerCase().includes(q) ||
        (c.region && c.region.toLowerCase().includes(q))
      );
      renderCityList(filtered);
    });
  }

  // ─── Scan Page for City Names ───
  function scanPageForCities() {
    if (!citiesData.length) return;

    // Build a lookup map from lowercase city name
    const cityLookup = {};
    citiesData.forEach(c => {
      cityLookup[c.name.toLowerCase()] = c;
    });

    // Find all elements that might contain city names
    // Look for itinerary headers, card titles, table cells, etc.
    const selectors = [
      '.itinerary-section-header h3',
      '.trip-card .card-body h4',
      '.billing-card__info h3',
      '.admin-table td strong',
      '[data-city-name]',
    ];

    selectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(el => {
        if (el.dataset.cityBound) return;

        const text = el.textContent.trim();

        // Try to match against known cities
        for (const [cityName, cityData] of Object.entries(cityLookup)) {
          if (text.toLowerCase().includes(cityName)) {
            el.dataset.cityName = cityData.name;
            el.dataset.cityBound = 'true';
            el.style.cursor = 'pointer';
            el.style.borderBottom = '1px dashed var(--accent)';
            el.title = `📍 Click to locate ${cityData.name} on map`;

            el.addEventListener('click', (e) => {
              e.preventDefault();
              e.stopPropagation();
              flyToCity(cityData);
            });
            break;
          }
        }
      });
    });
  }

  // ─── Global click handler for [data-city-name] ───
  document.addEventListener('click', (e) => {
    const el = e.target.closest('[data-city-name]');
    if (!el) return;
    const name = el.dataset.cityName.toLowerCase();
    if (markers[name]) {
      flyToCity(markers[name].city);
    }
  });

  // ─── Init ───
  toggle.addEventListener('click', togglePanel);
  fetchCities();
})();
