export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const AUTH_COOKIE_NAME = 'auth_token';
const USER_COOKIE_NAME = 'auth_user';

const setCookie = (name: string, value: string, days: number = 7): void => {
  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
  document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires.toUTCString()};path=/;SameSite=Strict`;
};

const getCookie = (name: string): string | null => {
  const nameEQ = `${name}=`;
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const c = cookie.trim();
    if (c.indexOf(nameEQ) === 0) {
      return decodeURIComponent(c.substring(nameEQ.length));
    }
  }
  return null;
};

const deleteCookie = (name: string): void => {
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
};

export const getAuthToken = (): string | null => {
  return getCookie(AUTH_COOKIE_NAME);
};

export const setAuthToken = (token: string): void => {
  setCookie(AUTH_COOKIE_NAME, token);
};

export const clearAuthToken = (): void => {
  deleteCookie(AUTH_COOKIE_NAME);
  deleteCookie(USER_COOKIE_NAME);
};

export const createBearerToken = (userId: string): string => {
  const payload = JSON.stringify({ user_id: userId });
  return btoa(payload);
};

export const getStoredUser = (): string | null => {
  return getCookie(USER_COOKIE_NAME);
};

export const setStoredUser = (user: string): void => {
  setCookie(USER_COOKIE_NAME, user);
};
