const DAY_MS = 24 * 60 * 60 * 1000;

function roundCost(value) {
  return Math.round(value * 100) / 100;
}

function addTokens(target, row) {
  target.input += row.input;
  target.cacheRead += row.cacheRead;
  target.output += row.output;
  target.total += row.total;
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

export function resolvePeriod(tokenRows, usageSummary, options) {
  if (options.allTime) {
    if (tokenRows.length === 0) {
      const now = new Date();
      const start = utcDayStart(now);
      return { start, end: addUtcDays(start, 1), label: 'Cursor 导出范围', fill: false };
    }
    let minDate = tokenRows[0].date;
    let maxDate = tokenRows[0].date;
    for (const row of tokenRows) {
      if (row.date < minDate) minDate = row.date;
      if (row.date > maxDate) maxDate = row.date;
    }
    const start = utcDayStart(minDate);
    const end = addUtcDays(utcDayStart(maxDate), 1);
    return { start, end, label: 'Cursor 导出范围', fill: false };
  }

  if (options.days) {
    const end = addUtcDays(utcDayStart(), 1);
    const start = addUtcDays(end, -options.days);
    return { start, end, label: `最近 ${options.days} 天`, fill: true };
  }

  const start = usageSummary?.billingCycleStart ?? new Date(Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), 1));
  const end = usageSummary?.billingCycleEnd ?? new Date(Date.UTC(start.getUTCFullYear(), start.getUTCMonth() + 1, 1));
  return { start, end, label: `${formatDay(start)} 到 ${formatDay(end)}（当前月）`, fill: true };
}

function dayRangeForChart(period) {
  if (!period.fill) return null;
  const chartEnd = new Date(Math.min(period.end.getTime(), addUtcDays(utcDayStart(), 1).getTime()));
  return { start: period.start, end: chartEnd };
}

function buildCostMaps(dailySpend) {
  const byDay = new Map();
  const byModel = new Map();
  let totalCents = 0;
  for (const entry of dailySpend) {
    if (!entry.category || !Number.isFinite(entry.dayMs)) continue;
    const day = new Date(entry.dayMs).toISOString().slice(0, 10);
    const cents = entry.spendCents || 0;
    byDay.set(day, (byDay.get(day) ?? 0) + cents);
    byModel.set(entry.category, (byModel.get(entry.category) ?? 0) + cents);
    totalCents += cents;
  }
  return { byDay, byModel, totalCents };
}

function buildDailySeries(byDay, costByDay, dayRange) {
  if (!dayRange) {
    return [...byDay.values()].sort((a, b) => a.key.localeCompare(b.key));
  }
  const items = [];
  for (let day = dayRange.start; day < dayRange.end; day = addUtcDays(day, 1)) {
    const key = formatDay(day);
    const tokens = byDay.get(key) ?? emptyUsage(key);
    const item = { ...tokens, key, cost: roundCost((costByDay.get(key) ?? 0) / 100) };
    items.push(item);
  }
  return items;
}

export function summarize(tokenRows, dailySpend, usageSummary, options = {}) {
  const period = resolvePeriod(tokenRows, usageSummary, options);
  const { start, end } = period;

  const total = emptyUsage('total');
  const byModelMap = new Map();
  const byDayMap = new Map();

  for (const row of tokenRows) {
    if (row.date < start || row.date >= end) continue;
    addTokens(total, row);
    if (!byModelMap.has(row.model)) byModelMap.set(row.model, emptyUsage(row.model));
    if (!byDayMap.has(row.day)) byDayMap.set(row.day, emptyUsage(row.day));
    addTokens(byModelMap.get(row.model), row);
    addTokens(byDayMap.get(row.day), row);
  }

  const { byDay: costByDay, byModel: costByModel, totalCents } = buildCostMaps(dailySpend);

  total.cost = roundCost(totalCents / 100);

  const sortUsage = (items) => [...items].sort((a, b) => b.total - a.total || a.key.localeCompare(b.key));

  const byModel = sortUsage(byModelMap.values()).map((item) => ({
    ...item,
    cost: roundCost((costByModel.get(item.key) ?? 0) / 100),
  }));

  const byDay = [...byDayMap.values()]
    .map((item) => ({ ...item, cost: roundCost((costByDay.get(item.key) ?? 0) / 100) }))
    .sort((a, b) => b.key.localeCompare(a.key));

  const dailySeries = buildDailySeries(byDayMap, costByDay, dayRangeForChart(period));

  return {
    generatedAt: new Date().toISOString(),
    period: period.label,
    total,
    byModel,
    byDay,
    dailySeries,
  };
}
