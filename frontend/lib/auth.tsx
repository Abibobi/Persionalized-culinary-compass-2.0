"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

export type AuthUser = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
};

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, refresh: string, user: AuthUser) => void;
  logout: () => void;
};

let activeToken: string | null = null;

export const setAuthToken = (token: string | null) => {
  activeToken = token;
};

export const getAuthToken = () => activeToken;

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setTokenState] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  // Restore session from localStorage on mount
  useEffect(() => {
    try {
      const savedToken = localStorage.getItem("pcc_access");
      const savedUser = localStorage.getItem("pcc_user");
      if (savedToken && savedUser) {
        activeToken = savedToken;
        setTokenState(savedToken);
        setUser(JSON.parse(savedUser));
      }
    } catch {
      // noop
    }
    setReady(true);
  }, []);

  const login = useCallback((accessToken: string, refreshToken: string, userData: AuthUser) => {
    activeToken = accessToken;
    setTokenState(accessToken);
    setUser(userData);
    localStorage.setItem("pcc_access", accessToken);
    localStorage.setItem("pcc_refresh", refreshToken);
    localStorage.setItem("pcc_user", JSON.stringify(userData));
  }, []);

  const logout = useCallback(() => {
    activeToken = null;
    setTokenState(null);
    setUser(null);
    localStorage.removeItem("pcc_access");
    localStorage.removeItem("pcc_refresh");
    localStorage.removeItem("pcc_user");
  }, []);

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: !!token && !!user,
      login,
      logout,
    }),
    [user, token, login, logout]
  );

  if (!ready) return null;

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
