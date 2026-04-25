import type { ErrorResponse } from "./types";

export const ENDPOINT_PREFIX = "/zotero-add-local-file";
export const TOKEN_PREF = "extensions.zoteroAddLocalFile.token";

export function jsonResponse(status: number, body: unknown): [number, Record<string, string>, string] {
  return [
    status,
    {
      "Content-Type": "application/json; charset=utf-8",
      "Access-Control-Allow-Origin": "null"
    },
    JSON.stringify(body, null, 2)
  ];
}

export function errorResponse(status: number, error: string): [number, Record<string, string>, string] {
  const body: ErrorResponse = { ok: false, error };
  return jsonResponse(status, body);
}

export function bearerToken(headers: Record<string, string | undefined>): string | null {
  const value = headers.authorization ?? headers.Authorization;
  if (!value) {
    return null;
  }
  const match = /^Bearer\s+(.+)$/i.exec(value.trim());
  return match ? match[1] : null;
}

export function configuredToken(): string | null {
  const token = Zotero.Prefs.get(TOKEN_PREF, true);
  if (typeof token !== "string" || !token.trim()) {
    return null;
  }
  return token.trim();
}

export function isAuthorized(headers: Record<string, string | undefined>): boolean {
  const expected = configuredToken();
  if (!expected) {
    return false;
  }
  return bearerToken(headers) === expected;
}

