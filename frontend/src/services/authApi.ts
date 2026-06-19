import type {
  LoginRequest,
  PasswordChangeRequest,
  RegisterRequest,
  TokenResponse,
  User,
  UserUpdate,
} from "@/types/auth";
import apiClient from "./apiClient";

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<TokenResponse>("/auth/login", data).then((r) => r.data),

  register: (data: RegisterRequest) =>
    apiClient.post<TokenResponse>("/auth/register", data).then((r) => r.data),

  me: () =>
    apiClient.get<User>("/auth/me").then((r) => r.data),

  updateMe: (data: UserUpdate) =>
    apiClient.patch<User>("/auth/me", data).then((r) => r.data),

  changePassword: (data: PasswordChangeRequest) =>
    apiClient.post("/auth/me/change-password", data).then((r) => r.data),

  listUsers: () =>
    apiClient.get<User[]>("/auth/users").then((r) => r.data),

  updateUser: (id: string, data: UserUpdate) =>
    apiClient.patch<User>(`/auth/users/${id}`, data).then((r) => r.data),

  deleteUser: (id: string) =>
    apiClient.delete(`/auth/users/${id}`).then((r) => r.data),
};
