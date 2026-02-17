const query = new URLSearchParams(window.location.search);
const API_BASE = query.get("apiBase") || "http://127.0.0.1:8000";

const presetEl = document.getElementById("preset");
const formEl = document.getElementById("scf-form");
const runButtonEl = document.getElementById("run-button");
const statusEl = document.getElementById("status-pill");
const summaryEl = document.getElementById("summary");
const rawJsonEl = document.getElementById("raw-json");
const orbitalBodyEl = document.querySelector("#orbital-table tbody");
const logScaleEl = document.getElementById("log-density-scale");
const FALLBACK_PRESETS = [
  { symbol: "H", atomic_number: 1, electrons: 1 },
  { symbol: "He+", atomic_number: 2, electrons: 1 },
  { symbol: "He", atomic_number: 2, electrons: 2 },
  { symbol: "Li", atomic_number: 3, electrons: 3 },
  { symbol: "Be", atomic_number: 4, electrons: 4 },
  { symbol: "Ne", atomic_number: 10, electrons: 10 },
];
let latestResult = null;

function setStatus(kind, text) {
  statusEl.className = `status ${kind}`;
  statusEl.textContent = text;
}

function numberValue(id) {
  return Number(document.getElementById(id).value);
}

function positiveNumberValue(id, fieldLabel) {
  const raw = document.getElementById(id).value.trim().replace(",", ".");
  const parsed = Number(raw);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    throw new Error(`${fieldLabel} must be a positive number (for example: 1e-6 or 0.001).`);
  }
  return parsed;
}

function boolValue(id) {
  return Boolean(document.getElementById(id).checked);
}

function formatFloat(value, digits = 6) {
  return Number(value).toFixed(digits);
}

function formatAxisNumber(value) {
  const absValue = Math.abs(value);
  if (absValue >= 100) {
    return value.toFixed(0);
  }
  if (absValue >= 10) {
    return value.toFixed(1);
  }
  if (absValue >= 1) {
    return value.toFixed(2);
  }
  if (absValue >= 0.1) {
    return value.toFixed(3);
  }
  return value.toExponential(1);
}

function formatScientific(value) {
  if (!Number.isFinite(value) || value <= 0) {
    return "0";
  }
  const exponent = Math.floor(Math.log10(value));
  const mantissa = value / 10 ** exponent;
  const roundedMantissa = Math.round(mantissa * 10) / 10;

  if (Math.abs(roundedMantissa - 1) < 1e-9) {
    return `1e${exponent}`;
  }
  return `${roundedMantissa}e${exponent}`;
}

function addUniqueTick(ticks, value) {
  const exists = ticks.some((tick) => Math.abs(tick - value) < 1e-9);
  if (!exists) {
    ticks.push(value);
  }
}

function buildLogTickValues(yMin, yMax, maxTicks = 7) {
  const ticks = [];
  const expStart = Math.ceil(yMin);
  const expEnd = Math.floor(yMax);

  for (let exponent = expStart; exponent <= expEnd; exponent += 1) {
    ticks.push(exponent);
  }

  if (ticks.length > maxTicks) {
    const step = Math.ceil(ticks.length / maxTicks);
    const reduced = ticks.filter((_, index) => index % step === 0);
    if (reduced[reduced.length - 1] !== ticks[ticks.length - 1]) {
      reduced.push(ticks[ticks.length - 1]);
    }
    ticks.length = 0;
    ticks.push(...reduced);
  }

  if (ticks.length === 0) {
    ticks.push(yMin, yMax);
  } else {
    addUniqueTick(ticks, yMin);
    addUniqueTick(ticks, yMax);
  }

  return ticks.sort((a, b) => a - b);
}

async function callBridge(method, payload = null) {
  await ensureBridgeReady();
  const pywebviewApi = window.pywebview && window.pywebview.api;
  if (pywebviewApi && typeof pywebviewApi[method] === "function") {
    if (payload === null || payload === undefined) {
      return pywebviewApi[method]();
    }
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
  let presets = [];
  try {
    presets = await callBridge("get_presets");
  } catch (error) {
    console.warn("Falling back to built-in presets:", error);
    presets = FALLBACK_PRESETS;
  }

  if (!Array.isArray(presets) || presets.length === 0) {
    presets = FALLBACK_PRESETS;
  }

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

  const margin = { left: 64, right: 20, top: 18, bottom: 44 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;

  const x = result.radial_grid;
  const y = result.density;

  if (!x || !y || x.length < 2) {
    return;
  }

  const useLogScale = !logScaleEl || logScaleEl.checked;
  const xMin = x[0];
  const xMax = x[x.length - 1];

  let yValues;
  let yMin;
  let yMax;
  let yAxisLabel;

  if (useLogScale) {
    const positive = y.filter((value) => value > 0);
    if (positive.length === 0) {
      return;
    }

    const yMaxLinear = Math.max(...positive);
    const yMinPositive = Math.min(...positive);
    const yFloor = Math.max(yMinPositive * 1e-3, 1e-18);

    yValues = y.map((value) => Math.log10(Math.max(value, yFloor)));
    yMin = Math.log10(yFloor);
    yMax = Math.log10(yMaxLinear);
    yAxisLabel = "n(r) (log)";
  } else {
    yValues = y;
    yMin = 0;
    yMax = Math.max(...y) || 1;
    yAxisLabel = "n(r)";
  }

  if (!Number.isFinite(yMin) || !Number.isFinite(yMax) || yMax <= yMin) {
    yMax = yMin + 1;
  }

  const xSpan = xMax - xMin || 1;
  const ySpan = yMax - yMin || 1;
  const px = (value) => margin.left + ((value - xMin) / xSpan) * plotWidth;
  const py = (value) => margin.top + (1 - (value - yMin) / ySpan) * plotHeight;

  const xTickCount = 7;
  const xTicks = [];
  for (let idx = 0; idx < xTickCount; idx += 1) {
    xTicks.push(xMin + (idx / (xTickCount - 1)) * xSpan);
  }
  const yTicks = useLogScale
    ? buildLogTickValues(yMin, yMax, 7)
    : Array.from({ length: 6 }, (_, idx) => yMin + (idx / 5) * ySpan);

  const xAxisY = margin.top + plotHeight;
  const yAxisX = margin.left;

  // Grid lines
  ctx.strokeStyle = "rgba(31, 47, 43, 0.14)";
  ctx.lineWidth = 1;
  for (const tick of xTicks) {
    const xPos = px(tick);
    ctx.beginPath();
    ctx.moveTo(xPos, margin.top);
    ctx.lineTo(xPos, xAxisY);
    ctx.stroke();
  }
  for (const tick of yTicks) {
    const yPos = py(tick);
    ctx.beginPath();
    ctx.moveTo(yAxisX, yPos);
    ctx.lineTo(yAxisX + plotWidth, yPos);
    ctx.stroke();
  }

  // Axes
  ctx.strokeStyle = "rgba(31, 47, 43, 0.55)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(yAxisX, margin.top);
  ctx.lineTo(yAxisX, xAxisY);
  ctx.lineTo(yAxisX + plotWidth, xAxisY);
  ctx.stroke();

  // Tick marks and tick labels
  ctx.font = "11px 'IBM Plex Sans', sans-serif";
  ctx.fillStyle = "rgba(31, 47, 43, 0.85)";
  ctx.strokeStyle = "rgba(31, 47, 43, 0.55)";
  ctx.lineWidth = 1;

  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  for (const tick of xTicks) {
    const xPos = px(tick);
    ctx.beginPath();
    ctx.moveTo(xPos, xAxisY);
    ctx.lineTo(xPos, xAxisY + 4);
    ctx.stroke();
    const label = formatAxisNumber(tick);
    ctx.fillText(label, xPos, xAxisY + 7);
  }

  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for (const tick of yTicks) {
    const yPos = py(tick);
    ctx.beginPath();
    ctx.moveTo(yAxisX - 4, yPos);
    ctx.lineTo(yAxisX, yPos);
    ctx.stroke();
    const label = useLogScale ? formatScientific(10 ** tick) : formatAxisNumber(tick);
    ctx.fillText(label, yAxisX - 8, yPos);
  }

  ctx.strokeStyle = "#006e7f";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(px(x[0]), py(yValues[0]));

  const stride = Math.max(1, Math.floor(x.length / 500));
  for (let i = stride; i < x.length; i += stride) {
    ctx.lineTo(px(x[i]), py(yValues[i]));
  }
  ctx.lineTo(px(x[x.length - 1]), py(yValues[yValues.length - 1]));
  ctx.stroke();

  const baseline = useLogScale ? yMin : 0;
  ctx.fillStyle = "rgba(0, 110, 127, 0.08)";
  ctx.lineTo(px(x[x.length - 1]), py(baseline));
  ctx.lineTo(px(x[0]), py(baseline));
  ctx.closePath();
  ctx.fill();

  ctx.fillStyle = "#1f2f2b";
  ctx.font = "12px 'IBM Plex Sans', sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  ctx.fillText("r (a.u.)", margin.left + plotWidth / 2, height - 18);
  ctx.save();
  ctx.translate(16, margin.top + plotHeight / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  ctx.fillText(yAxisLabel, 0, 0);
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
      density_tolerance: positiveNumberValue("density-tolerance", "Density tolerance"),
      l_max: numberValue("l-max"),
      states_per_l: numberValue("states-per-l"),
      use_hartree: boolValue("use-hartree"),
      use_exchange: boolValue("use-exchange"),
      use_correlation: boolValue("use-correlation"),
    },
  };

  try {
    const data = await callBridge("run_scf", payload);

    latestResult = data;
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
if (logScaleEl) {
  logScaleEl.addEventListener("change", () => {
    if (latestResult) {
      drawDensityPlot(latestResult);
    }
  });
}
init();
