export interface AuthenticationState {
  type: "session";
  authenticated: boolean;
}

export interface AuthenticatedUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name?: string;
  is_active: boolean;
}

export interface AuthenticatedOrganization {
  id: string;
  name: string;
  country?: string;
  currency?: string;
  timezone?: string;
  is_active?: boolean;
}

export interface AuthenticatedRole {
  id: string;
  name: string;
  is_active?: boolean;
  permissions: string[];
  permissions_by_module?: Record<
    string,
    string[]
  >;
}

export interface AuthenticationContext {
  authentication: AuthenticationState;
  user: AuthenticatedUser;
  organization: AuthenticatedOrganization;
  role: AuthenticatedRole;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoggedOutUser {
  id: string;
  email: string;
}

export interface LogoutData {
  authentication: AuthenticationState;
  logged_out_user: LoggedOutUser;
}

export interface LogoutAllData {
  authentication: AuthenticationState;
  logged_out_user?: LoggedOutUser;
  sessions_revoked?: number;
  revoked_sessions?: number;
}