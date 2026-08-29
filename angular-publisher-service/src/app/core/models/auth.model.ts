export interface AuthenticationRequest {
  username: string;
  password: string;
}

export interface AuthToken {
  accessToken: string;
  tokenType: string;
  expiresAt: string;
  adminId: number;
}

export interface AdminProfile {
  adminId: number;
  username: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}