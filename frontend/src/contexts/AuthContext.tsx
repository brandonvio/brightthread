import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { User } from '../types/models';
import { setAuthToken, clearAuthToken, createBearerToken, getAuthToken, getStoredUser, setStoredUser } from '../api/config';
import { login as apiLogin } from '../api/authApi';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Restore user from cookie on mount
  useEffect(() => {
    const token = getAuthToken();
    const storedUser = getStoredUser();

    if (token && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser) as User;
        setUser(parsedUser);
      } catch {
        // Invalid stored user, clear everything
        clearAuthToken();
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    const response = await apiLogin(email, password);
    const token = createBearerToken(response.user.id);
    setAuthToken(token);
    setStoredUser(JSON.stringify(response.user));
    setUser(response.user);
  };

  const logout = (): void => {
    clearAuthToken();
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: user !== null,
    login,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
