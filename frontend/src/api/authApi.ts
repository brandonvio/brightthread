import { post } from './client';
import type { User } from '../types/models';

export interface LoginResponse {
  user: User;
}

export const login = async (email: string, password: string): Promise<LoginResponse> => {
  return post<LoginResponse>('/v1/auth/login', { email, password });
};
