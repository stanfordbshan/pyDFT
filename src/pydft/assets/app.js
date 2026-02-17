const query = new URLSearchParams(window.location.search);
const API_BASE = query.get("apiBase") || "http://127.0.0.1:8000";

const presetEl = document.getElementById("preset");
const formEl = document.getElementById("scf-form");
const runButtonEl = document.getElementById("run-button");
const statusEl = document.getElementById("status-pill");
const summaryEl = document.getElementById("summary");
const rawJsonEl = document.getElementById("raw-json");
const orbitalBodyEl = document.querySelector("#orbital-table tbody");

function setStatus(kind, text) {
  statusEl.className = `status ${kind}`;
  statusEl.textContent = text;
}

function numberValue(id) {
  return Number(document.getElementById(id).value);
}

function boolValue(id) {
  return Boolean(document.getElementById(id).checked);
}

function formatFloat(value, digits = 6) {
  return Number(value).toFixed(digits);
}

async function callBridge(method, payload = null) {
  await ensureBridgeReady();
  const pywebviewApi = window.pywebview && window.pywebview.api;
  if (pywebviewApi && typeof pywebviewApi[method] === "function") {
    return pywebviewApi[method](payload);
  }

  // Browser fallback path for local API-server development.
  if (method === "get_presets") {
    const response = await fetch(`${API_BASE}/api/v1/presets`);
    if (!response.ok) {
      throw new Error(`Failed to load presets: ${response.status}`);
    }
    return response.json();
  }

  if (method === "run_scf") {
    const response = await fetch(`${API_BASE}/api/v1/scf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || `Request failed (${response.status})`);
    }
    return data;
  }

  throw new Error(`Unsupported bridge method: ${method}`);
}

async function ensureBridgeReady() {
  if (!window.pywebview) {
    return;
  }
  if (window.pywebview.api) {
    return;
  }

  await new Promise((resolve) => {
    window.addEventListener("pywebviewready", resolve, { once: true });
  });
}

async function loadPresets() {
  const presets = await callBridge("get_presets");
  presetEl.innerHTML = "";

  for (const preset of presets) {
    const option = document.createElement("option");
    option.value = preset.symbol;
    option.textContent = `${preset.symbol} (Z=${preset.atomic_number}, N=${preset.electrons})`;
    option.dataset.atomicNumber = String(preset.atomic_number);
    option.dataset.electrons = String(preset.electrons);
    presetEl.appendChild(option);
  }

  presetEl.addEventListener("change", () => {
    const selected = presetEl.selectedOptions[0];
    document.getElementById("atomic-number").value = selected.dataset.atomicNumber;
    document.getElementById("electrons").value = selected.dataset.electrons;
  });

  if (presetEl.options.length > 0) {
    presetEl.selectedIndex = 0;
    presetEl.dispatchEvent(new Event("change"));
  }
}

function renderSummary(result) {
  summaryEl.innerHTML = `
    <div class="summary-grid">
      <div class="metric">
        <div class="label">System</div>
        <div class="value">${result.system.symbol} (Z=${result.system.atomic_number}, N=${result.system.electrons})</div>
      </div>
      <div class="metric">
        <div class="label">Converged</div>
        <div class="value">${result.converged ? "Yes" : "No"}</div>
      </div>
      <div class="metric">
        <div class="label">Iterations</div>
        <div class="value">${result.iterations}</div>
      </div>
      <div class="metric">
        <div class="label">Total Energy (Ha)</div>
        <div class="value">${formatFloat(result.total_energy, 8)}</div>
      </div>
      <div class="metric">
        <div class="label">Density Residual</div>
        <div class="value">${Number(result.density_residual).toExponential(3)}</div>
      </div>
    </div>
  `;
}

function renderOrbitals(result) {
  orbitalBodyEl.innerHTML = "";
  for (const orbital of result.orbitals) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${orbital.n_index}</td>
      <td>${orbital.l}</td>
      <td>${formatFloat(orbital.occupancy, 1)}</td>
      <td>${formatFloat(orbital.energy, 8)}</td>
    `;
    orbitalBodyEl.appendChild(row);
  }
}

function drawDensityPlot(result) {
  const canvas = document.getElementById("density-plot");
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  ctx.clearRect(0, 0, width, height);

  const margin = { left: 48, right: 18, top: 18, bottom: 30 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;

  const x = result.radial_grid;
  const y = result.density;

  if (!x || !y || x.length < 2) {
    return;
  }

  const xMin = x[0];
  const xMax = x[x.length - 1];
  const yMax = Math.max(...y) || 1;

  const px = (value) => margin.left + ((value - xMin) / (xMax - xMin)) * plotWidth;
  const py = (value) => margin.top + (1 - value / yMax) * plotHeight;

  ctx.strokeStyle = "rgba(31, 47, 43, 0.45)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(margin.left, margin.top);
  ctx.lineTo(margin.left, margin.top + plotHeight);
  ctx.lineTo(margin.left + plotWidth, margin.top + plotHeight);
  ctx.stroke();

  ctx.strokeStyle = "#006e7f";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(px(x[0]), py(y[0]));

  const stride = Math.max(1, Math.floor(x.length / 500));
  for (let i = stride; i < x.length; i += stride) {
    ctx.lineTo(px(x[i]), py(y[i]));
  }
  ctx.lineTo(px(x[x.length - 1]), py(y[y.length - 1]));
  ctx.stroke();

  ctx.fillStyle = "rgba(0, 110, 127, 0.08)";
  ctx.lineTo(px(x[x.length - 1]), margin.top + plotHeight);
  ctx.lineTo(px(x[0]), margin.top + plotHeight);
  ctx.closePath();
  ctx.fill();

  ctx.fillStyle = "#1f2f2b";
  ctx.font = "12px 'IBM Plex Sans', sans-serif";
  ctx.fillText("r (a.u.)", margin.left + plotWidth / 2 - 18, height - 8);
  ctx.save();
  ctx.translate(12, margin.top + plotHeight / 2 + 16);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText("n(r)", 0, 0);
  ctx.restore();
}

async function runCalculation(event) {
  event.preventDefault();
  runButtonEl.disabled = true;
  setStatus("running", "Running");

  const payload = {
    symbol: presetEl.value,
    atomic_number: numberValue("atomic-number"),
    electrons: numberValue("electrons"),
    parameters: {
      r_max: numberValue("r-max"),
      num_points: numberValue("num-points"),
      max_iterations: numberValue("max-iterations"),
      density_mixing: numberValue("density-mixing"),
      density_tolerance: numberValue("density-tolerance"),
      l_max: numberValue("l-max"),
      states_per_l: numberValue("states-per-l"),
      use_hartree: boolValue("use-hartree"),
      use_exchange: boolValue("use-exchange"),
      use_correlation: boolValue("use-correlation"),
    },
  };

  try {
    const data = await callBridge("run_scf", payload);

    renderSummary(data);
    renderOrbitals(data);
    drawDensityPlot(data);
    rawJsonEl.textContent = JSON.stringify(data, null, 2);
    setStatus(data.converged ? "ok" : "error", data.converged ? "Converged" : "Not Converged");
  } catch (error) {
    setStatus("error", "Error");
    summaryEl.innerHTML = `<p>${error.message}</p>`;
  } finally {
    runButtonEl.disabled = false;
  }
}

async function init() {
  try {
    setStatus("running", "Connecting");
    await ensureBridgeReady();
    await loadPresets();
    setStatus("idle", "Idle");
  } catch (error) {
    setStatus("error", "Unavailable");
    summaryEl.innerHTML = `<p>${error.message}</p>`;
  }
}

formEl.addEventListener("submit", runCalculation);
init();
