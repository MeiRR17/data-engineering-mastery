"use strict";

const $ = (id) => document.getElementById(id);
const number = new Intl.NumberFormat("en-US");
const decimal = new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 });
let recentEvents = [];

async function config() {
  if (window.DATAPULSE_CONFIG?.url && window.DATAPULSE_CONFIG?.publishableKey) {
    return window.DATAPULSE_CONFIG;
  }
  const result = await fetch("/api/config", { cache: "no-store" });
  if (!result.ok) throw new Error("Supabase configuration missing. Configure Vercel environment variables or web/config.local.js.");
  const data = await result.json();
  return { url: data.url, publishableKey: data.publishableKey };
}

async function select(cfg, route) {
  const response = await fetch(`${cfg.url.replace(/\/$/, "")}/rest/v1/${route}`, {
    headers: { apikey: cfg.publishableKey, Accept: "application/json" },
    cache: "no-store",
  });
  if (!response.ok) throw new Error(`Supabase returned HTTP ${response.status} for ${route.split("?")[0]}`);
  return response.json();
}

function setStatus(message, state) {
  $("status").textContent = message;
  $("dot").className = `dot ${state}`;
}

function addCell(row, value, className = "") {
  const td = document.createElement("td");
  if (className) td.className = className;
  td.textContent = value;
  row.appendChild(td);
}

function renderRows(filterText = "") {
  const root = $("rows");
  root.replaceChildren();
  const filtered = recentEvents.filter((r) => (r.place ?? "").toLowerCase().includes(filterText.toLowerCase()));
  if (!filtered.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.textContent = "No events to display";
    row.appendChild(cell);
    root.appendChild(row);
    return;
  }
  for (const event of filtered) {
    const row = document.createElement("tr");
    addCell(row, new Date(event.observed_at).toISOString().slice(0, 16).replace("T", " "));
    addCell(row, event.place ?? "Unknown");
    addCell(row, event.magnitude === null ? "—" : decimal.format(event.magnitude), event.magnitude >= 5 ? "mag high" : "mag");
    addCell(row, event.depth_km === null ? "—" : decimal.format(event.depth_km));
    root.appendChild(row);
  }
}

function renderChart(days) {
  const root = $("chart");
  root.replaceChildren();
  const ordered = [...days].reverse();
  const max = Math.max(1, ...ordered.map((row) => Number(row.total_events)));
  for (const row of ordered) {
    const item = document.createElement("div");
    item.className = "bar-col";
    const total = Number(row.total_events);
    const label = document.createElement("strong");
    label.textContent = number.format(total);
    const bar = document.createElement("div");
    bar.className = "bar";
    bar.style.height = `${Math.max(2, Math.round((total / max) * 174))}px`;
    bar.title = `${row.day}: ${total} events`;
    const date = document.createElement("span");
    date.textContent = row.day.slice(5);
    item.append(label, bar, date);
    root.appendChild(item);
  }
  if (!ordered.length) root.textContent = "No data has been loaded yet.";
}

async function refresh() {
  $("refresh").disabled = true;
  setStatus("Synchronizing data…", "");
  try {
    const isDemo = new URLSearchParams(window.location.search).get("demo") === "1";
    let days, events;
    if (isDemo) {
      const response = await fetch("./demo-data.json");
      if (!response.ok) throw new Error("Demo data unavailable");
      const demo = await response.json();
      days = demo.daily_stats;
      events = demo.earthquakes;
      document.querySelector(".source-label").textContent = "Synthetic data · DEMO";
    } else {
      const cfg = await config();
      [days, events] = await Promise.all([
        select(cfg, "daily_stats?select=day,total_events,magnitude_count,avg_magnitude,max_magnitude&order=day.desc&limit=14"),
        select(cfg, "earthquakes?select=event_id,observed_at,magnitude,place,depth_km&order=observed_at.desc&limit=40"),
      ]);
    }
    const total = days.reduce((sum, r) => sum + Number(r.total_events), 0);
    const maximum = Math.max(...days.map((r) => r.max_magnitude == null ? -Infinity : Number(r.max_magnitude)));
    const validDays = days.filter((r) => r.avg_magnitude != null);
    const totalMeasured = validDays.reduce((sum, r) => sum + Number(r.magnitude_count), 0);
    const exactAverage = totalMeasured ? validDays.reduce((sum, r) => sum + Number(r.avg_magnitude) * Number(r.magnitude_count), 0) / totalMeasured : null;
    $("event-count").textContent = number.format(total);
    $("max-mag").textContent = Number.isFinite(maximum) ? decimal.format(maximum) : "—";
    $("avg-mag").textContent = exactAverage === null ? "—" : decimal.format(exactAverage);
    $("last-event").textContent = events.length ? new Date(events[0].observed_at).toISOString().slice(5, 16).replace("T", " ") : "—";
    recentEvents = events;
    renderRows($("filter").value);
    renderChart(days);
    setStatus(isDemo ? "Demo mode — synthetic data only" : `Dashboard updated · ${new Date().toLocaleTimeString("en-US")}`, "ok");
  } catch (error) {
    console.error(error);
    setStatus(`Error: ${error.message}`, "error");
    $("rows").replaceChildren();
  } finally {
    $("refresh").disabled = false;
  }
}

$("refresh").addEventListener("click", refresh);
$("filter").addEventListener("input", (event) => renderRows(event.target.value));
refresh();
