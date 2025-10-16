import { request } from "./client";

export type LoginInput = {
  username: string;
  password: string;
};

export type TokenResponse = {
  token: string;
  expires_at: string;
};

export const login = async (credentials: LoginInput): Promise<TokenResponse> => {
  return request<TokenResponse>("/tokens", {
    method: "POST",
    body: JSON.stringify(credentials)
  });
};
