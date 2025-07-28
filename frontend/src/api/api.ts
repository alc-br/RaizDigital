import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

// Attach token if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface UserCreateDTO {
  email: string;
  full_name?: string;
  password: string;
}

export async function registerUser(data: UserCreateDTO) {
  const res = await api.post('/auth/register', data);
  return res.data;
}

export async function loginUser(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  const res = await api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return res.data as { access_token: string; refresh_token: string };
}

export async function forgotPassword(email: string) {
  const res = await api.post('/auth/forgot-password', { email });
  return res.data;
}

export async function resetPassword(token: string, newPassword: string) {
  const res = await api.post('/auth/reset-password', { token, new_password: newPassword });
  return res.data;
}

export async function refreshAccessToken(refreshToken: string) {
  const res = await api.post('/auth/refresh', { token: refreshToken });
  return res.data as { access_token: string; refresh_token: string };
}

export async function updateProfile(data: any) {
  const res = await api.put('/users/me', data);
  return res.data;
}

export async function getCurrentUser() {
  const res = await api.get('/users/me');
  return res.data;
}

export interface OrderCreateDTO {
  target_name: string;
  order_price: number;
  target_dob_approx?: string;
  target_city?: string;
  target_state?: string;
  target_parents_names?: string;
  additional_info?: string;
}

export async function createOrder(data: OrderCreateDTO) {
  const res = await api.post('/orders/', data);
  return res.data;
}

export async function fetchOrders() {
  const res = await api.get('/orders/');
  return res.data;
}

export async function fetchOrderDetail(orderId: number) {
  const res = await api.get(`/orders/${orderId}`);
  return res.data;
}

export async function createCheckoutSession(orderId: number) {
  // In a real implementation, this would call a backend endpoint to create a Stripe session
  const res = await api.post('/checkout/create-session', { order_id: orderId });
  return res.data;
}

export default api;
