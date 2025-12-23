import { get, post } from './client';
import type { User, CreateUserRequest } from '../types/models';

interface UserListResponse {
  users: User[];
  total: number;
}

export const getUsers = async (): Promise<User[]> => {
  const response = await get<UserListResponse>('/v1/users');
  return response.users;
};

export const getUsersByCompany = async (companyId: string): Promise<User[]> => {
  const response = await get<UserListResponse>(`/v1/users/company/${companyId}`);
  return response.users;
};

export const getUser = async (userId: string): Promise<User> => {
  return get<User>(`/v1/users/${userId}`);
};

export const createUser = async (data: CreateUserRequest): Promise<User> => {
  return post<User>('/v1/users', data);
};
