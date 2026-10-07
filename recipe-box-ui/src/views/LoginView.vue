<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/tools/useAuth';
import { useNotifications } from '@/tools/useNotifications';
import RegisterModal from '@/components/RegisterModal.vue';
import BaseModal from '@/components/BaseModal.vue';

const email = ref('');
const password = ref('');
const showRegisterModal = ref(false);

const router = useRouter();
const { login, authStatus, authError } = useAuth();
const { showToast } = useNotifications();

const isSubmitting = computed(() => authStatus.value === 'authenticating');

async function handleSubmit(e: Event) {
    e.preventDefault();
    if (!email.value || !password.value) {
        return;
    }
    await login(email.value, password.value);

    if (authStatus.value === 'authenticated') {
        router.push('/app');
    }
}
    
function openRegister() {
    showRegisterModal.value = true;
}

function closeRegister() {
    showRegisterModal.value = false;
}

</script>

<template> 
    <section class="login-view__container">
        <h1 class="login-view__label">LOGIN</h1>

        <form class="login-form" @submit="handleSubmit">
            <div class="login-form__email-box">
                <label class="login-form__email-label" for="email">Email</label>
                <input class="login-form__email-input" id="email" type="email"  v-model="email", autocomplete="email" />
            </div>
            <div class="login-form__password-box">
                <label class="login-form__password-label" for="password">Password</label>
                <input class="login-form__password-input" id="password" type="password" v-model="password" autocomplete="current-password" />
            </div>

            <p v-if="authError" style="color: red;">
                {{ authError }}
            </p>
             <button type="submit" :disabled="isSubmitting">
                {{ isSubmitting ? 'Logging in...' : 'Login' }}
             </button>

             <button type="button" @click="openRegister">
                Register
             </button>
        </form>

        <RegisterModal
            v-if="showRegisterModal"
            @close="closeRegister" />
    </section>
</template>