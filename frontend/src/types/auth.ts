export type UserRole = "admin" | "manager" | "user";

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  name: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface UserUpdate {
  name?: string;
  is_active?: boolean;
  role?: UserRole;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}
