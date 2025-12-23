import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios';
import { API_BASE_URL, getAuthToken } from './config';

export const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  client.interceptors.request.use((config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  return client;
};

export const apiClient = createApiClient();

export const get = async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  const response = await apiClient.get<T>(url, config);
  return response.data;
};

export const post = async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
  const response = await apiClient.post<T>(url, data, config);
  return response.data;
};

export const patch = async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
  const response = await apiClient.patch<T>(url, data, config);
  return response.data;
};

export const del = async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  const response = await apiClient.delete<T>(url, config);
  return response.data;
};
