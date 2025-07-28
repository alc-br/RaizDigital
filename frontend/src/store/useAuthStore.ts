import { create } from 'zustand';

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  setTokens: (token: string | null, refreshToken: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  refreshToken: typeof window !== 'undefined' ? localStorage.getItem('refreshToken') : null,
  setTokens: (token, refreshToken) => {
    if (typeof window !== 'undefined') {
      if (token) localStorage.setItem('token', token);
      else localStorage.removeItem('token');
      if (refreshToken) localStorage.setItem('refreshToken', refreshToken);
      else localStorage.removeItem('refreshToken');
    }
    set({ token, refreshToken });
  },
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
    }
    set({ token: null, refreshToken: null });
  },
}));
