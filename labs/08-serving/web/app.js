"use strict";

// Never turn API values into HTML. All user-visible data goes through textContent.
const byId = (id) => document.getElementById(id);
const num = new Intl.NumberFormat("he-IL");
const decimal = new Intl.NumberFormat("he-IL", {maximumFractionDigits: 2});
let eventRows = [];

async function getJSON(route) {
  const response = await fetch(route, {cache: "no-store"});
  if (!response.ok) throw new Error("HTTP " + response.status);
  return response.json();
}

function setText(id, value) {
  byId(id).textContent = value;
}

function utc(value) {
  if (!value) return "—";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime())
    ? "—" : parsed.toISOString().slice(0, 16).replace("T", " ") + "Z";
}

function renderFreshness(data) {
  const panel = byId("freshness-panel");
  const states = {
    fresh: ["נתונים עדכניים ביחס לשעון הדוגמה", "שעת האירוע האחרון נמצאת בתוך חלון העדכניות."],
    stale: ["אזהרה: המידע מיושן", "אל תפרש את המספרים כנתונים בזמן אמת."],
    future: ["אזהרה: זמן אירוע עתידי", "יש לבדוק את שעוני המקור וה־Pipeline."],
    empty: ["אין אירועים להצגה", "ייתכן שה־Pipeline טרם פרסם נתונים."]
  };
  const state = states[data.freshness_status] ? data.freshness_status : "empty";
  const values = states[state];
  panel.dataset.state = state;
  setText("freshness-title", values[0]);
  const age = data.age_hours == null ? "" : " גיל אירוע אחרון: " +
    decimal.format(data.age_hours) + " שעות.";
  const blocked = data.last_quality_status === "blocked"
    ? " ההרצה האחרונה נחסמה בשער איכות הנתונים." : "";
  setText("freshness-details", values[1] + age + blocked +
    " נתונים סינתטיים בלבד; סף לימודי: " + data.freshness_limit_hours + " שעות.");
}

function renderChart(items) {
  const root = byId("daily-chart");
  root.replaceChildren();
  if (!items.length) {
    root.textContent = "אין נתונים להציג.";
    return;
  }
  const days = [...items].reverse();
  const maximum = Math.max(1, ...days.map((r) => Number(r.total_events)));
  for (const item of days) {
    const holder = document.createElement("div");
    holder.className = "chart-item";
    const count = document.createElement("strong");
    count.className = "chart-value";
    count.textContent = num.format(item.total_events);
    const bar = document.createElement("div");
    bar.className = "chart-bar";
    bar.style.height = Math.max(5, Math.round(147 * item.total_events / maximum)) + "px";
    bar.title = String(item.day_utc) + ": " + String(item.total_events);
    const label = document.createElement("span");
    label.className = "chart-label";
    label.textContent = String(item.day_utc).slice(5);
    holder.append(count, bar, label);
    root.appendChild(holder);
  }
}

function renderQuality(items) {
  const root = byId("quality-runs");
  root.replaceChildren();
  if (!items.length) {
    root.textContent = "עדיין אין בדיקות איכות.";
    return;
  }
  for (const item of items) {
    const container = document.createElement("div");
    container.className = "quality-item";
    const description = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = item.run_id;
    const details = document.createElement("p");
    const failures = item.issue_codes.length ? " · סיבות: " + item.issue_codes.join(", ") : "";
    details.textContent = "תקינות: " + num.format(item.valid_rows) +
      " · הסגר: " + num.format(item.quarantined_rows) +
      " · פורסמו: " + num.format(item.published_rows) + failures;
    description.append(title, details);
    const state = document.createElement("span");
    state.className = "quality-state" + (item.status === "blocked" ? " blocked" : "");
    state.textContent = item.status === "passed" ? "עבר" : "נחסם";
    container.append(description, state);
    root.appendChild(container);
  }
}

function appendCell(row, value) {
  const td = document.createElement("td");
  td.textContent = value;
  row.appendChild(td);
}

function renderEvents(filter = "") {
  const root = byId("events");
  root.replaceChildren();
  const term = filter.toLowerCase().trim();
  const selected = eventRows.filter((item) =>
    item.event_id.toLowerCase().includes(term) ||
    item.region_code.toLowerCase().includes(term));
  if (!selected.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 4;
    td.textContent = "לא נמצאו אירועים תואמים.";
    tr.appendChild(td);
    root.appendChild(tr);
    return;
  }
  for (const item of selected) {
    const tr = document.createElement("tr");
    appendCell(tr, item.event_id);
    appendCell(tr, utc(item.observed_at));
    appendCell(tr, item.region_code);
    appendCell(tr, item.magnitude == null ? "—" : decimal.format(item.magnitude));
    root.appendChild(tr);
  }
}

async function refresh() {
  byId("refresh").disabled = true;
  byId("system-status").className = "system-status";
  setText("system-status", "טוען נתונים מה־API המקומי…");
  try {
    const [overview, daily, events, quality] = await Promise.all([
      getJSON("/api/v1/overview"), getJSON("/api/v1/daily?limit=14"),
      getJSON("/api/v1/events?limit=20"), getJSON("/api/v1/quality?limit=5")
    ]);
    if ([overview, daily, events, quality].some((obj) => obj.dataset !== "synthetic-training")) {
      throw new Error("Unexpected data source");
    }
    setText("event-count", num.format(overview.total_events));
    setText("magnitude-avg", overview.average_magnitude === null
      ? "—" : decimal.format(overview.average_magnitude));
    setText("magnitude-known", num.format(overview.known_magnitude_events));
    setText("last-event", utc(overview.latest_event_at));
    renderFreshness(overview);
    renderChart(daily.items);
    renderQuality(quality.items);
    eventRows = events.items;
    renderEvents(byId("filter").value);
    setText("system-status", "API לקריאה בלבד · מקור: SQLite מקומי · נתונים סינתטיים");
  } catch (_error) {
    byId("system-status").className = "system-status error";
    setText("system-status", "לא ניתן לטעון את נתוני ההדגמה. בדוק את שרת ה־API ונסה שוב.");
    byId("freshness-panel").dataset.state = "unavailable";
    setText("freshness-title", "נתונים לא זמינים — אין להסיק מסקנות");
    setText("freshness-details", "השרת אינו זמין או מחזיר שגיאה. מוצגת הודעת כשל במקום נתונים ישנים.");
    setText("event-count", "—");
    setText("magnitude-avg", "—");
    setText("magnitude-known", "—");
    setText("last-event", "—");
    byId("daily-chart").replaceChildren();
    byId("quality-runs").replaceChildren();
    eventRows = [];
    renderEvents();
  } finally {
    byId("refresh").disabled = false;
  }
}

byId("refresh").addEventListener("click", refresh);
byId("filter").addEventListener("input", (event) => renderEvents(event.target.value));
refresh();

