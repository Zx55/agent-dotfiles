#!/usr/bin/env node
import { cursorStateDbPath, readAccessToken, fetchUsageCsv, parseUsageRows, fetchUsageSummary, fetchDailySpendByCategory } from './lib/data.mjs';
import { renderMarkdown } from './lib/render.mjs';
import { summarize, resolvePeriod } from './lib/summary.mjs';

const DEFAULT_MONTHLY_BUDGET_USD = 2_000;

function budgetFromEnv() {
  const value = Number.parseFloat(process.env.CURSOR_USAGE_MONTHLY_BUDGET_USD || '');
  return Number.isFinite(value) && value > 0 ? value : DEFAULT_MONTHLY_BUDGET_USD;
}

const args = new Set(process.argv.slice(2));
const asJson = args.has('--json');
const allTime = args.has('--all');
const daysArg = process.argv.find((arg) => arg.startsWith('--days='));
const days = daysArg ? Number.parseInt(daysArg.slice('--days='.length), 10) : null;
const options = { allTime, days: Number.isFinite(days) && days > 0 ? days : null };

async function main() {
  const dbPath = cursorStateDbPath();
  if (!dbPath) {
    throw new Error('Cursor state.vscdb not found. Open Cursor and sign in first, or set CURSOR_STATE_DB_PATH.');
  }

  const token = readAccessToken(dbPath);
  if (!token) {
    throw new Error(`Cursor access token not found in ${dbPath}. Try signing in to Cursor again.`);
  }

  const [csv, usageSummary] = await Promise.all([
    fetchUsageCsv(token),
    fetchUsageSummary(token),
  ]);
  const tokenRows = parseUsageRows(csv);

  const period = resolvePeriod(tokenRows, usageSummary, options);
  const dailySpend = await fetchDailySpendByCategory(token, {
    periodStartMs: period.start.getTime(),
    periodEndMs: period.end.getTime(),
    groupBy: 1,
    spendType: 3,
  });

  const summary = summarize(tokenRows, dailySpend.dailySpend, usageSummary, options);
  summary.budget = usageSummary && typeof usageSummary.limitCents === 'number'
    ? usageSummary.limitCents / 100
    : budgetFromEnv();

  process.stdout.write(asJson ? `${JSON.stringify(summary, null, 2)}\n` : `${renderMarkdown(summary)}\n`);
}

main().catch((error) => {
  process.stderr.write(`cursor-usage: ${error.message || error}\n`);
  process.exitCode = 1;
});
