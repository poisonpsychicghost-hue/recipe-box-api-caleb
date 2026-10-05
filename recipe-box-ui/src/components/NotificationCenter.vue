<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useNotifications } from '@/tools/useNotifications';

const router = useRouter();
const { toasts, activeModal, clear } = useNotifications()

function closeToast(id: number) {
    const idx = toasts.value.findIndex(t => t.id === id);
    if (idx !== -1) {
        toasts.value.splice(idx, 1);
    }
}

function handleModalConfirm() {
    if (!activeModal.value) return;

    const modal = activeModal.value;

    if (modal.onConfirm) {
        modal.onConfirm();
    }

    if (modal.type === 'session-expired') {
        router.push('/login');
    }

    clear();
}

function handleModalCancel() {
    const modal = activeModal.value;
    if (!modal) {
        clear();
        return;
    }
    if (modal?.onCancel) {
        modal.onCancel();
    }

    if (modal.type === 'session-expired') {
        router.push('/login')
    }
    
    clear()
}

</script>

<template>
        <!-- Notification Toasts-->
        <div class="toast-container">
            <div 
            v-for="toast in toasts"
            :key="toast.id"
            class="toast"
            :data-type="toast.type"
            >
            <span>{{ toast.message }}</span>
            <button type="button"
            @click="closeToast(toast.id)">x</button>
        </div>
        </div>

        <!--Modals -->
        <div v-if="activeModal" class="modal-backdrop">
            <div class="modal">
                <h2>{{ activeModal.title }}</h2>
                <p>{{ activeModal.message }}</p>
                <div class="modal-actions">
                    <button type="button"
                    @click="handleModalConfirm">ok</button>
                    <button type="button"
                    @click="handleModalCancel">Cancel</button>
                </div>
            </div>
        </div>
</template>