<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/tools/useAuth';

const email = ref('');
const password = ref('');

const router = useRouter();
const { login, authStatus, authError } = useAuth();

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
    


</script>

<template> 
    <section>
        <h1>LOGIN</h1>

        <form @submit="handleSubmit">
            <div>
                <label for="email">Email</label>
                <input id="email" type="email"  v-model="email", autocomplete="email" />
            </div>
            <div>
                <label for="password">Password</label>
                <input id="password" type="password" v-model="password" autocomplete="current-password" />
            </div>

            <p v-if="authError" style="color: red;">
                {{ authError }}
            </p>
             <button type="submit" :disabled="isSubmitting">
                {{ isSubmitting ? 'Logging in...' : 'Login' }}
             </button>

             <button type="button">
                Register
             </button>
        </form>
    </section>

</template>