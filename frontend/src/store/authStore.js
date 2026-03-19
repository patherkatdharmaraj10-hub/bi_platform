import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from '../api/axios';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email, password) => {
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);
  
  const res = await axios.post('/api/v1/auth/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  
  const { access_token, user_id, role, full_name } = res.data;
  axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
  set({
    token: access_token,
    user: { id: user_id, email, role, full_name },
    isAuthenticated: true,
  });
  return res.data;
},

      logout: () => {
        delete axios.defaults.headers.common['Authorization'];
        set({ user: null, token: null, isAuthenticated: false });
      },

      // Role checkers
      isAdmin:   () => get().user?.role === 'admin',
      isAnalyst: () => ['admin', 'analyst'].includes(get().user?.role),
      isViewer:  () => ['admin', 'analyst', 'viewer'].includes(get().user?.role),
    }),
    { name: 'bi-auth' }
  )
);