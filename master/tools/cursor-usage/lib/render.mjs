const DASHBOARD_URL = 'https://cursor.com/dashboard/usage';
const DAILY_CHART_WIDTH = 32;
const DEFAULT_MONTHLY_BUDGET_USD = 2_000;

function monthlyBudgetUsd() {
  const value = Number.parseFloat(process.env.CURSOR_USAGE_MONTHLY_BUDGET_USD || '');
  return Number.isFinite(value) && value > 0 ? value : DEFAULT_MONTHLY_BUDGET_USD;
}

function formatNumber(value) {
  return new Intl.NumberFormat('en-US').format(value);
}

function formatCost(value) {
  return `US$${value.toFixed(2)}`;
}

function formatBudget(value) {
  return `$${new Intl.NumberFormat('en-US', {
    maximumFractionDigits: value % 1 === 0 ? 0 : 2,
    minimumFractionDigits: value % 1 === 0 ? 0 : 2,
  }).format(value)}`;
}

function formatPercent(value) {
  return `${value.toFixed(value >= 10 ? 1 : 2)}%`;
}

function tokenBreakdown(usage) {
  return `总计 ${formatNumber(usage.total)} tokens，输入 ${formatNumber(usage.input)} tokens，缓存 ${formatNumber(usage.cacheRead)} tokens，输出 ${formatNumber(usage.output)} tokens`;
}

function modelLine(usage) {
  return `${usage.key}：${formatNumber(usage.total)} tokens，${formatCost(usage.cost)}（输入 ${formatNumber(usage.input)}，缓存 ${formatNumber(usage.cacheRead)}，输出 ${formatNumber(usage.output)}）`;
}

function formatCompactNumber(value) {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return String(value);
}

function renderDailyChart(items) {
  const maxTotal = Math.max(0, ...items.map((item) => item.total));
  if (items.length === 0 || maxTotal === 0) {
    return ['没有找到可绘制的每日用量记录。'];
  }

  return items.map((item) => {
    const barLength = item.total === 0 ? 0 : Math.max(1, Math.round((item.total / maxTotal) * DAILY_CHART_WIDTH));
    const bar = '#'.repeat(barLength).padEnd(DAILY_CHART_WIDTH, ' ');
    return `${item.key} | ${bar} | ${formatCompactNumber(item.total)} tokens，${formatCost(item.cost)}`;
  });
}

export function renderMarkdown(summary) {
  const budget = monthlyBudgetUsd();
  const budgetPercent = budget > 0 ? (summary.total.cost / budget) * 100 : 0;
  const lines = [
    '# 周期统计',
    '',
    `* 统计周期：${summary.period}`,
    `* 生成日期：${summary.generatedAt}`,
    `* Tokens：${tokenBreakdown(summary.total)}`,
    `* 额度：${formatBudget(summary.total.cost)}/${formatBudget(budget)} (${formatPercent(budgetPercent)} used)`,
    `* Dashboard：${DASHBOARD_URL}`,
    '',
    '# 每日用量趋势',
    '',
    '```text',
    ...renderDailyChart(summary.dailySeries),
    '```',
    '',
    '# 按模型统计',
  ];

  if (summary.byModel.length === 0) {
    lines.push('', '没有找到用量记录。');
  } else {
    for (const item of summary.byModel.slice(0, 20)) {
      lines.push(`* ${modelLine(item)}`);
    }
  }
  return lines.join('\n');
}
