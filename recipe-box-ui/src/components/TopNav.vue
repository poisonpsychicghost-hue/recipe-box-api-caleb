<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '@/tools/useAuth';
import { useTheme } from '@/tools/useTheme';

type TabKey = 'search' | 'add' | 'list' | 'settings' | 'admin'

const props = defineProps<{
    activeTab: TabKey
}>()
const emit = defineEmits<{
    (e: 'change-tab', tab: 'search' | 'add' | 'list' | 'settings' | 'admin'): void
}>()

const tabs: { key: TabKey; label: string}[] =[
    {key: 'search', label: 'Search'}, 
    {key: 'add', label: 'Add'},
    {key: 'list', label: 'List'},
    {key: 'settings', label: 'Settings'},
    {key: 'admin', label: 'Admin'}, // obfuscate with admin only
]

const router = useRouter();
const { currentUser, logout } = useAuth();
const { isDarkMode, toggleDarkmode } = useTheme();

const username = computed(() => currentUser.value?.username ?? 'Guest');
const role = computed(() => currentUser.value?.role ?? 'guest');

const roleLabel = computed(() => {
    const r = role.value;
    if (r === 'admin') return 'Admin';
    if (r === 'user') return 'Member';
    return 'Guest';
});

const showAdminTab = computed(() => role.value === 'admin');

function goTab(tab: 'search' | 'add' | 'list' | 'settings' | 'admin') {
    emit('change-tab', tab);
}

function handleLogout() {
    logout();
    router.push('/login');
}

</script>

<template>
        <nav class="top-nav">
            <div class="top-nav__left">
                <span class="top-nav__brand">🐶🐶🐶 Sirius Recipe Box</span>
            </div>

            <div class="top-nav__center">
                <button type="button" :class="{ active: activeTab === 'search' }" @click="goTab('search')">
                    Search
                </button>
                <button type="button" :class="{ active: activeTab === 'list'}" @click="goTab('list')">
                    List
                </button>
                <button type="button" :class="{ active: activeTab === 'add'}" @click="goTab('add')">
                    Add
                </button>
                <button type="button" :class="{ active: activeTab === 'settings'}" @click="goTab('settings')">
                    Settings
                </button>
                <button v-if="showAdminTab" type="button" :class="{ active: activeTab === 'admin'}" @click="goTab('admin')">
                    Admin
                </button>
            </div>
            <div class="top-nav__right">
                <button type="button" @click="toggleDarkmode">
                    {{ isDarkMode ? '☀️' : '🌙' }}
                </button>
                <span class="top-nav__user">
                    {{ username }}
                <span class="top-nav__role">
                    {{ roleLabel }}
                </span>
                </span>
                <button type="button" @click="handleLogout">
                    Logout
                </button>
            </div>
        </nav>
</template>