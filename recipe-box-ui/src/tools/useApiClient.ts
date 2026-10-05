import { useAuth } from "./useAuth";
import { useNotifications } from "./useNotifications";

const API_BASE = 'http://127.0.0.1:5000';

interface ApiResult<T> {
    data: T | null;
    status: number;
    error: string | null;
}

export function useApiClient() {
    const { getAuthHeader, handleTokenExpired } = useAuth();
    const { showToast } = useNotifications();

    async function request<T>(
        path: string,
        options: RequestInit = {}
    ): Promise<ApiResult<T>> {
        const url = `${API_BASE}${path}`;

        const headers: HeadersInit = {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
            ...getAuthHeader(),
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });

            let data: any = null;
            try{
                data = await response.json();
            } catch {
                data = null
            }

            if (response.status === 401) {
                handleTokenExpired();
                return {
                    data: null,
                    status: response.status,
                    error: 'Unauthorized. Session may have expired.'
                };
            }

            if (!response.ok) {
                const message = data?.error || data?.message || `Request Failed with status: ${response.status}`;

                showToast({ type: 'error', message})

                return {
                    data: null,
                    status: response.status,
                    error: message,
                };
            }

            return {
                data: data as T,
                status: response.status,
                error: null,
            };
        } catch (err) {
            const message = 'Network error while contacting the API';
            showToast({ type: 'error', message });

            return {
                data: null,
                status: 0,
                error: message,
            };
        }
    }

    return {
        request,
    }
}
