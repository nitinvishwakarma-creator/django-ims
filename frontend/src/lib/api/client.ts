import type {
  APIErrorResponse,
  APIResponse,
  APISuccessResponse,
  CSRFData,
} from "@/lib/api/types";

const configuredBaseURL =
  process.env.NEXT_PUBLIC_API_BASE_URL;

if (!configuredBaseURL) {
  throw new Error(
    "NEXT_PUBLIC_API_BASE_URL is not configured.",
  );
}

export const API_BASE_URL =
  configuredBaseURL.replace(/\/+$/, "");

const UNSAFE_METHODS = new Set([
  "POST",
  "PUT",
  "PATCH",
  "DELETE",
]);

let cachedCSRFToken: string | null = null;

export class APIRequestError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details?: Record<string, unknown>;
  readonly requestId?: string;

  constructor({
    status,
    code,
    message,
    details,
    requestId,
  }: {
    status: number;
    code: string;
    message: string;
    details?: Record<string, unknown>;
    requestId?: string;
  }) {
    super(message);

    this.name = "APIRequestError";
    this.status = status;
    this.code = code;
    this.details = details;
    this.requestId = requestId;
  }
}

function buildURL(path: string): string {
  const normalizedPath = path.startsWith("/")
    ? path
    : `/${path}`;

  return `${API_BASE_URL}${normalizedPath}`;
}

function isUnsafeMethod(method: string): boolean {
  return UNSAFE_METHODS.has(
    method.toUpperCase(),
  );
}

async function parseAPIResponse<T>(
  response: Response,
): Promise<APIResponse<T>> {
  const contentType =
    response.headers.get("content-type") ?? "";

  if (!contentType.includes("application/json")) {
    throw new APIRequestError({
      status: response.status,
      code: "INVALID_API_RESPONSE",
      message:
        "The server returned an invalid response.",
    });
  }

  return (await response.json()) as APIResponse<T>;
}

export function clearCSRFToken(): void {
  cachedCSRFToken = null;
}

export async function getCSRFToken(
  forceRefresh = false,
): Promise<string> {
  if (cachedCSRFToken && !forceRefresh) {
    return cachedCSRFToken;
  }

  const response = await fetch(
    buildURL("/auth/csrf/"),
    {
      method: "GET",
      credentials: "include",
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    },
  );

  const body =
    await parseAPIResponse<CSRFData>(response);

  if (!response.ok || !body.success) {
    const errorBody = body as APIErrorResponse;

    throw new APIRequestError({
      status: response.status,
      code:
        errorBody.error?.code ??
        "CSRF_BOOTSTRAP_FAILED",
      message:
        errorBody.error?.message ??
        "Unable to initialize CSRF protection.",
      details: errorBody.error?.details,
      requestId: errorBody.request_id,
    });
  }

  const token = body.data.csrf.token;

  if (!token) {
    throw new APIRequestError({
      status: response.status,
      code: "CSRF_TOKEN_MISSING",
      message:
        "The server did not return a CSRF token.",
      requestId: body.request_id,
    });
  }

  cachedCSRFToken = token;

  return token;
}

export interface APIRequestOptions
  extends Omit<RequestInit, "body"> {
  body?: unknown;
}

export async function apiRequest<T>(
  path: string,
  options: APIRequestOptions = {},
  retryCSRF = true,
): Promise<APISuccessResponse<T>> {
  const method = (
    options.method ?? "GET"
  ).toUpperCase();

  const headers = new Headers(
    options.headers,
  );

  headers.set(
    "Accept",
    "application/json",
  );

  let requestBody: BodyInit | undefined;

  if (options.body !== undefined) {
    headers.set(
      "Content-Type",
      "application/json",
    );

    requestBody = JSON.stringify(
      options.body,
    );
  }

  if (isUnsafeMethod(method)) {
    const csrfToken =
      await getCSRFToken();

    headers.set(
      "X-CSRFToken",
      csrfToken,
    );
  }

  const response = await fetch(
    buildURL(path),
    {
      ...options,
      method,
      headers,
      body: requestBody,
      credentials: "include",
      cache: options.cache ?? "no-store",
    },
  );

  const body =
    await parseAPIResponse<T>(response);

  if (!response.ok || !body.success) {
    const errorBody = body as APIErrorResponse;

    if (
      response.status === 403 &&
      errorBody.error?.code === "CSRF_FAILED" &&
      isUnsafeMethod(method) &&
      retryCSRF
    ) {
      clearCSRFToken();

      await getCSRFToken(true);

      return apiRequest<T>(
        path,
        options,
        false,
      );
    }

    throw new APIRequestError({
      status: response.status,
      code:
        errorBody.error?.code ??
        "API_REQUEST_FAILED",
      message:
        errorBody.error?.message ??
        "The API request failed.",
      details: errorBody.error?.details,
      requestId: errorBody.request_id,
    });
  }

  return body;
}