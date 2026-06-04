import { copyFileSync, existsSync, mkdtempSync, rmSync } from 'node:fs';
import { homedir, tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { DatabaseSync } from 'node:sqlite';

const STATE_DB_RELATIVE = join('User', 'globalStorage', 'state.vscdb');
const ACCESS_TOKEN_KEY = 'cursorAuth/accessToken';
const SESSION_COOKIE = 'WorkosCursorSessionToken';
const FETCH_TIMEOUT_MS = 10_000;

function defaultStateDbPath() {
  if (process.platform === 'darwin') {
    return join(homedir(), 'Library', 'Application Support', 'Cursor', STATE_DB_RELATIVE);
  }
  if (process.platform === 'win32') {
    const appData = process.env.APPDATA?.trim() || join(homedir(), 'AppData', 'Roaming');
    return join(appData, 'Cursor', STATE_DB_RELATIVE);
  }
  const xdgConfigHome = process.env.XDG_CONFIG_HOME?.trim() || join(homedir(), '.config');
  return join(xdgConfigHome, 'Cursor', STATE_DB_RELATIVE);
}

export function cursorStateDbPath() {
  const explicit = process.env.CURSOR_STATE_DB_PATH?.trim();
  if (explicit) {
    const resolved = resolve(explicit);
    return existsSync(resolved) ? resolved : null;
  }

  const configDirs = process.env.CURSOR_CONFIG_DIR?.trim();
  const candidates = configDirs
    ? configDirs
        .split(',')
        .map((value) => value.trim())
        .filter(Boolean)
        .map((value) => {
          const resolved = resolve(value);
          return resolved.endsWith('.vscdb') ? resolved : join(resolved, STATE_DB_RELATIVE);
        })
    : [defaultStateDbPath()];

  return candidates.find((candidate) => existsSync(candidate)) || null;
}

function queryAccessToken(dbPath) {
  const db = new DatabaseSync(dbPath, { readOnly: true });
  try {
    const row = db
      .prepare('SELECT value FROM ItemTable WHERE key = ? LIMIT 1')
      .get(ACCESS_TOKEN_KEY);
    return typeof row?.value === 'string' ? row.value.trim() || null : null;
  } finally {
    db.close();
  }
}

export function readAccessToken(dbPath) {
  try {
    return queryAccessToken(dbPath);
  } catch (error) {
    if (!/database is locked/i.test(String(error?.message || error))) {
      throw error;
    }

    const snapshotDir = mkdtempSync(join(tmpdir(), 'cursor-usage-'));
    const snapshotDb = join(snapshotDir, 'state.vscdb');
    try {
      copyFileSync(dbPath, snapshotDb);
      for (const suffix of ['-shm', '-wal']) {
        const companion = `${dbPath}${suffix}`;
        if (existsSync(companion)) copyFileSync(companion, `${snapshotDb}${suffix}`);
      }
      return queryAccessToken(snapshotDb);
    } finally {
      rmSync(snapshotDir, { recursive: true, force: true });
    }
  }
}

function decodeJwtSub(token) {
  const payload = token.split('.')[1];
  if (!payload) return null;
  try {
    const b64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = b64.padEnd(Math.ceil(b64.length / 4) * 4, '=');
    const json = JSON.parse(Buffer.from(padded, 'base64').toString('utf8'));
    return typeof json.sub === 'string' ? json.sub.trim() : null;
  } catch {
    return null;
  }
}

export async function fetchUsageCsv(token) {
  const baseUrl = (process.env.CURSOR_WEB_BASE_URL?.trim() || 'https://cursor.com').replace(/\/+$/, '');
  const url = `${baseUrl}/api/dashboard/export-usage-events-csv?strategy=tokens`;
  const sub = decodeJwtSub(token);
  const cookieValues = sub ? [token, `${sub}::${token}`] : [token];
  const attempts = [{ Authorization: `Bearer ${token}` }];

  for (const cookieValue of cookieValues) {
    attempts.push({ Cookie: `${SESSION_COOKIE}=${cookieValue}` });
    attempts.push({
      Authorization: `Bearer ${token}`,
      Cookie: `${SESSION_COOKIE}=${cookieValue}`,
    });
  }

  const failures = [];
  for (const headers of attempts) {
    const response = await fetch(url, {
      headers: { Accept: 'text/csv,*/*;q=0.8', ...headers },
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
    });
    if (response.ok) return response.text();
    failures.push(`${response.status} ${response.statusText}`);
  }

  throw new Error(`Cursor usage export auth failed: ${failures.join('; ')}`);
}

function parseCsv(text) {
  const rows = [];
  let field = '';
  let row = [];
  let inQuotes = false;
  let i = 0;

  while (i < text.length) {
    const char = text[i];
    if (inQuotes) {
      if (char === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i += 2;
          continue;
        }
        inQuotes = false;
        i++;
        continue;
      }
      field += char;
      i++;
      continue;
    }
    if (char === '"') {
      inQuotes = true;
      i++;
      continue;
    }
    if (char === ',') {
      row.push(field);
      field = '';
      i++;
      continue;
    }
    if (char === '\r') {
      i++;
      continue;
    }
    if (char === '\n') {
      row.push(field);
      rows.push(row);
      field = '';
      row = [];
      i++;
      continue;
    }
    field += char;
    i++;
  }

  if (field !== '' || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

function parseDate(value) {
  const text = String(value || '').trim();
  if (!text) return null;
  const date = /^\d{4}-\d{2}-\d{2}$/.test(text) ? new Date(`${text}T00:00:00Z`) : new Date(text);
  return Number.isNaN(date.getTime()) ? null : date;
}

function parseInteger(value) {
  const number = Number(String(value ?? '').replace(/,/g, '').trim());
  return Number.isFinite(number) && number > 0 ? Math.round(number) : 0;
}

function parseCost(value) {
  const number = Number(String(value ?? '').replace(/[$,]/g, '').trim());
  return Number.isFinite(number) && number > 0 ? number : 0;
}

export function parseUsageRows(csv) {
  const rows = parseCsv(csv);
  if (rows.length < 2) return [];

  const header = rows[0].map((name) => name.trim());
  const idx = (name) => header.indexOf(name);
  const indexes = {
    date: idx('Date'),
    model: idx('Model'),
    inputCacheWrite: idx('Input (w/ Cache Write)'),
    inputNoCache: idx('Input (w/o Cache Write)'),
    cacheRead: idx('Cache Read'),
    output: idx('Output Tokens'),
    cost: idx('Cost'),
  };

  if (indexes.date < 0 || indexes.model < 0) {
    throw new Error(`Cursor CSV did not contain expected Date/Model columns. Headers: ${header.join(', ')}`);
  }

  return rows.slice(1).flatMap((row) => {
    if (row.length === 1 && row[0].trim() === '') return [];
    const date = parseDate(row[indexes.date]);
    const model = row[indexes.model]?.trim();
    if (!date || !model) return [];

    const inputCacheWrite = indexes.inputCacheWrite >= 0 ? parseInteger(row[indexes.inputCacheWrite]) : 0;
    const inputNoCache = indexes.inputNoCache >= 0 ? parseInteger(row[indexes.inputNoCache]) : 0;
    const cacheRead = indexes.cacheRead >= 0 ? parseInteger(row[indexes.cacheRead]) : 0;
    const output = indexes.output >= 0 ? parseInteger(row[indexes.output]) : 0;
    const cost = indexes.cost >= 0 ? parseCost(row[indexes.cost]) : 0;
    const total = inputCacheWrite + inputNoCache + cacheRead + output;
    if (total === 0 && cost === 0) return [];

    return [{
      date,
      day: date.toISOString().slice(0, 10),
      model,
      input: inputCacheWrite + inputNoCache,
      cacheRead,
      output,
      total,
      cost,
    }];
  });
}
