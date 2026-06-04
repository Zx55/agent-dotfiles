const DAY_MS = 24 * 60 * 60 * 1000;

function roundCost(value) {
  return Math.round(value * 100) / 100;
}

function addUsage(target, row) {
  target.input += row.input;
  target.cacheRead += row.cacheRead;
  target.output += row.output;
  target.total += row.total;
  target.cost = roundCost(target.cost + row.cost);
  target.events += 1;
}

function emptyUsage(key) {
  return { key, input: 0, cacheRead: 0, output: 0, total: 0, cost: 0, events: 0 };
}

function formatDay(date) {
  return date.toISOString().slice(0, 10);
}

function addUtcDays(date, daysToAdd) {
  return new Date(date.getTime() + daysToAdd * DAY_MS);
}

function utcDayStart(date = new Date()) {
  return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
}

function currentMonthRange(now = new Date()) {
  const start = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1));
  const end = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 1));
  return { start, end };
}

function filterRows(rows, options) {
  if (options.allTime) {
    return {
      period: 'Cursor 导出范围',
      rows,
      dayRange: null,
    };
  }

  if (options.days) {
    const cutoff = Date.now() - options.days * DAY_MS;
    return {
      period: `最近 ${options.days} 天`,
      rows: rows.filter((row) => row.date.getTime() >= cutoff),
      dayRange: null,
    };
  }

  const { start, end } = currentMonthRange();
  const chartEnd = new Date(Math.min(end.getTime(), addUtcDays(utcDayStart(), 1).getTime()));
  return {
    period: `${formatDay(start)} 到 ${formatDay(end)}（当前月）`,
    rows: rows.filter((row) => row.date >= start && row.date < end),
    dayRange: { start, end: chartEnd },
  };
}

function dailySeries(byDay, dayRange) {
  if (!dayRange) {
    return [...byDay.values()].sort((a, b) => a.key.localeCompare(b.key));
  }

  const items = [];
  for (let day = dayRange.start; day < dayRange.end; day = addUtcDays(day, 1)) {
    const key = formatDay(day);
    items.push(byDay.get(key) || emptyUsage(key));
  }
  return items;
}

export function summarize(rows, options = {}) {
  const { period, rows: filtered, dayRange } = filterRows(rows, options);
  const total = emptyUsage('total');
  const byModel = new Map();
  const byDay = new Map();

  for (const row of filtered) {
    addUsage(total, row);
    if (!byModel.has(row.model)) byModel.set(row.model, emptyUsage(row.model));
    if (!byDay.has(row.day)) byDay.set(row.day, emptyUsage(row.day));
    addUsage(byModel.get(row.model), row);
    addUsage(byDay.get(row.day), row);
  }

  const sortUsage = (items) => [...items].sort((a, b) => b.total - a.total || a.key.localeCompare(b.key));
  return {
    generatedAt: new Date().toISOString(),
    period,
    total,
    byModel: sortUsage(byModel.values()),
    byDay: [...byDay.values()].sort((a, b) => b.key.localeCompare(a.key)),
    dailySeries: dailySeries(byDay, dayRange),
  };
}
