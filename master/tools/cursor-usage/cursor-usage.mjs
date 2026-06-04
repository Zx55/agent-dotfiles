#!/usr/bin/env node
import { cursorStateDbPath, fetchUsageCsv, parseUsageRows, readAccessToken } from './lib/data.mjs';
import { renderMarkdown } from './lib/render.mjs';
import { summarize } from './lib/summary.mjs';

const args = new Set(process.argv.slice(2));
const asJson = args.has('--json');
const allTime = args.has('--all');
const daysArg = process.argv.find((arg) => arg.startsWith('--days='));
const days = daysArg ? Number.parseInt(daysArg.slice('--days='.length), 10) : null;

async function main() {
  const dbPath = cursorStateDbPath();
  if (!dbPath) {
    throw new Error('Cursor state.vscdb not found. Open Cursor and sign in first, or set CURSOR_STATE_DB_PATH.');
  }

  const token = readAccessToken(dbPath);
  if (!token) {
    throw new Error(`Cursor access token not found in ${dbPath}. Try signing in to Cursor again.`);
  }

  const csv = await fetchUsageCsv(token);
  const rows = parseUsageRows(csv);
  const summary = summarize(rows, { allTime, days });
  process.stdout.write(asJson ? `${JSON.stringify(summary, null, 2)}\n` : `${renderMarkdown(summary)}\n`);
}

main().catch((error) => {
  process.stderr.write(`cursor-usage: ${error.message || error}\n`);
  process.exitCode = 1;
});
