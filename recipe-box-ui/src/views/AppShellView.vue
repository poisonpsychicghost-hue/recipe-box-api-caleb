<script setup lang="ts">
import { ref } from 'vue'

import TopNav from '@/components/TopNav.vue'
import NotificationCenter from '@/components/NotificationCenter.vue'
import BaseModal from '@/components/BaseModal.vue'
import { useAuth } from '@/tools/useAuth.ts'

import SearchView from './SearchView.vue'
import AddRecipeView from './AddRecipeView.vue'
import ListRecipesView from './ListRecipesView.vue'
import SettingsView from './SettingsView.vue'
import AdminView from './AdminView.vue'



type TabKey = 'search' | 'add' | 'list' | 'settings' | 'admin'

const activeTab = ref<TabKey>('search')
const auth = useAuth()

function handleTabChange(tab: TabKey) {
    activeTab.value = tab
}

</script>

<template>
    <TopNav :active-tab="activeTab"
    @change-tab="handleTabChange" />

    <section>
        <SearchView v-if="activeTab === 'search'" />
        <AddRecipeView v-else-if="activeTab === 'add'" />
        <ListRecipesView v-else-if="activeTab === 'list'" />
        <SettingsView v-else-if="activeTab === 'settings'" />
        <AdminView v-else-if="activeTab === 'admin'" />
    </section>

    <section>
        <button @click="auth.handleTokenExpired()">TEST EXPIRED</button>
        <NotificationCenter />
        <BaseModal />
    </section>

</template>