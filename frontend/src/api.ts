import type {
  AuditEvent,
  CaseSummary,
} from "./types";

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(
    `/api${path}`,
    {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    },
  );

  const text = await response.text();

  let body: unknown;

  try {
    body = text
      ? JSON.parse(text)
      : null;
  } catch {
    body = text;
  }

  if (!response.ok) {
    const detail =
      typeof body === "object"
      && body !== null
      && "detail" in body
        ? (
            body as {
              detail: unknown;
            }
          ).detail
        : body;

    throw new Error(
      typeof detail === "string"
        ? detail
        : `Request failed: ${response.status}`,
    );
  }

  return body as T;
}

export const api = {
  listCases: () =>
    request<CaseSummary[]>(
      "/cases",
    ),

  getCase: (
    id: string,
  ) =>
    request<CaseSummary>(
      `/cases/${id}`,
    ),

  createCase: (
    payload: {
      title: string;
      decision: string;
      context: string;
    },
  ) =>
    request<CaseSummary>(
      "/cases",
      {
        method: "POST",
        body: JSON.stringify(
          payload,
        ),
      },
    ),

  orchestrate: (
    id: string,
  ) =>
    request(
      `/cases/${id}/orchestrate`,
      {
        method: "POST",
      },
    ),

  audit: (
    id: string,
  ) =>
    request<AuditEvent[]>(
      `/cases/${id}/audit`,
    ),
};