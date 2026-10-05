import { ref } from 'vue';

type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: number;
  type: ToastType;
  message: string;
}

interface ModalConfig {
  type: string;
  title: string;
  message: string;
  onConfirm?: () => void;
  onCancel?: () => void;
}

const toasts = ref<Toast[]>([]);
const activeModal = ref<ModalConfig | null>(null);
let toastId = 0;

export function useNotifications() {
  function showToast(payload: { type: ToastType; message: string }) {
    // for now, just push into the list; UI will handle rendering
    toasts.value.push({ id: ++toastId, ...payload });
  }

  function showModal(config: ModalConfig) {
    activeModal.value = config;
  }

  function clear() {
    toasts.value = [];
    activeModal.value = null;
  }

  return {
    toasts,
    activeModal,
    showToast,
    showModal,
    clear,
  };
}