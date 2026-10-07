<script setup lang="ts">
import { ref } from 'vue';
import { useAuth } from '@/tools/useAuth'
import { useNotifications } from '@/tools/useNotifications';

const emit = defineEmits<{
    close: [];
}>();

const username = ref('');
const email = ref('');
const password = ref('');
const isSubmitting = ref(false);
const localError = ref<string | null>(null);

const { login } = useAuth();
const { showToast } = useNotifications();

const API_BASE = 'http://127.0.0.1:5000'

async function handleRegister(e: Event) {
    e.preventDefault();
    localError.value = null;

    if (!username.value || !email.value || !password.value ) {
        localError.value = 'All fields are required.';
        return;
    }

    isSubmitting.value = true;

    try {
        const response = await fetch(`${API_BASE}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username.value,
                email: email.value,
                password: password.value,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            const message = 
                data?.error ||
                data?.message ||
                'Registration Failed. Please try again.';
            localError.value = message;
            showToast({type: 'error', message});
            return;
        }

        //201 created Success
        showToast({
            type: 'success',
            message: data.message || 'User created successfully.',
        });

        // auto login with same email/password

        emit('close');
    } catch (err) {
        const message = 'Netword error during registration.';
        localError.value = message;
        showToast({ type: 'error', message});
    } finally {
        isSubmitting.value = false;
    }
}

function handleCancel() {
    emit('close');
}

</script>

<template>
    <div class="modal-backdrop">
        <div class="modal">
            <h2>Register</h2>
            <form @submit="handleRegister">
                <div class="reg-modal-username">
                    <label class="modal__label" for="reg-username">Username</label>
                    <input class="modal__input"
                        id="reg-username"
                        type="text"
                        v-model="username" />
                </div>
                <div class="reg-modal-email">
                    <label class="modal__label" for="reg-email">Email</label>
                    <input class="modal__input"
                        id="reg-email"
                        type="email"
                        v-model="email" />
                </div>

                <div class="reg-modal-password">
                    <label class="modal__label" for="reg-password">Password</label>
                    <input class="modal__input"
                        id="reg-password"
                        type="password"
                        v-model="password" />
                </div>

                <p v-if="localError" style="color: red;">{{ localError }}</p>
                <div>

                <div>
                    <button type="submit" :disabled="isSubmitting">
                        {{ isSubmitting ? 'Creating...' : 'Create Account' }}
                    </button>
                    <button type="button" @click="handleCancel">Cancel</button>
                </div>
                </div>
            </form>
        </div>
    </div>
</template>
