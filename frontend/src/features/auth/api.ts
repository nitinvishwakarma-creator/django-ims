import {
  apiRequest,
  clearCSRFToken,
  getCSRFToken,
} from "@/lib/api/client";

import type {
  AuthenticationContext,
  LoginCredentials,
  LogoutAllData,
  LogoutData,
} from "@/features/auth/types";

export async function initializeCSRF():
  Promise<string> {
  return getCSRFToken();
}

export async function login(
  credentials: LoginCredentials,
): Promise<AuthenticationContext> {
  const response =
    await apiRequest<AuthenticationContext>(
      "/auth/login/",
      {
        method: "POST",
        body: credentials,
      },
    );

  return response.data;
}

export async function getCurrentUser():
  Promise<AuthenticationContext> {
  const response =
    await apiRequest<AuthenticationContext>(
      "/auth/me/",
    );

  return response.data;
}

export async function logout():
  Promise<LogoutData> {
  try {
    const response =
      await apiRequest<LogoutData>(
        "/auth/logout/",
        {
          method: "POST",
        },
      );

    return response.data;
  } finally {
    clearCSRFToken();
  }
}

export async function logoutAll():
  Promise<LogoutAllData> {
  try {
    const response =
      await apiRequest<LogoutAllData>(
        "/auth/logout-all/",
        {
          method: "POST",
        },
      );

    return response.data;
  } finally {
    clearCSRFToken();
  }
}