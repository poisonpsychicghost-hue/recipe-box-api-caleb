import { ref, readonly } from 'vue';
import { useNotifications } from './useNotifications';

type AuthStatus = 'idle' | 'authenticating' | 'authenticated' | 'error';

interface User {
  id: number;
  email: string;
  role: string;
  username: string;
}

const authToken = ref<string | null>(null);
const currentUser = ref<User | null>(null);
const authStatus = ref<AuthStatus>('idle');
const authError = ref<string | null>(null);

const API_BASE = 'http://127.0.0.1:5000';

export function useAuth() {
  const { showToast, showModal } = useNotifications();

  async function login(email: string, password: string) {
    authStatus.value = 'authenticating';
    authError.value = null;

    try {
      const response = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        let message = 'Invalid credentials';

        try {
          const errBody = await response.json();
          if (typeof errBody?.message === 'string') {
            message = errBody.message;
          }
        } catch {
          // ignore JSON parse error
        }

        authStatus.value = 'error';
        authError.value = message;
        showToast({ type: 'error', message });
        return;
      }

      const data = await response.json();

      const token: string | undefined = data.token;
      const user: User = {
        id: data.id,
        email: data.email,
        role: data.role,
        username: data.username,
      };

      if (!token) {
        authStatus.value = 'error';
        const message = 'Login succeeded but no token was returned.';
        authError.value = message;
        showToast({ type: 'error', message });
        return;
      }

      authToken.value = token;
      currentUser.value = user;
      authStatus.value = 'authenticated';
      authError.value = null;

      showToast({
        type: 'success',
        message: `Welcome back, ${user.username}!`,
      });
    } catch (err) {
      authStatus.value = 'error';
      const message = 'Network error while trying to log in.';
      authError.value = message;
      showToast({ type: 'error', message });
    }
  }

  function logout() {
    authToken.value = null;
    currentUser.value = null;
    authStatus.value = 'idle';
    authError.value = null;

    showToast({ type: 'info', message: 'Logged out successfully.' });
  }

  function handleTokenExpired() {
    authToken.value = null;
    currentUser.value = null;
    authStatus.value = 'idle';
    authError.value = 'Session expired';

    showModal({
      type: 'session-expired',
      title: 'Session expired',
      message: 'Your session has expired. Please log in again to continue.',
    });
  }

  function getAuthHeader() {
    return authToken.value
      ? { Authorization: `Bearer ${authToken.value}` }
      : {};
  }

  return {
    authToken: readonly(authToken),
    currentUser: readonly(currentUser),
    authStatus: readonly(authStatus),
    authError: readonly(authError),
    login,
    logout,
    handleTokenExpired,
    getAuthHeader,
  };
}