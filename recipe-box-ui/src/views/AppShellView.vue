<script setup lang="ts">
import { ref } from 'vue'
import TopNav from '@/components/TopNav.vue'
type TabKey = 'search' | 'add' | 'list' | 'settings' | 'admin'

const activeTab = ref<TabKey>('search')

function handleTabChange(tab: TabKey) {
    activeTab.value = tab
}

</script>

<template>
    <TopNav :active-tab="activeTab"
    @change-tab="handleTabChange" />

    <section>
        <h1 v-if="activeTab === 'search'">Search View(Tab)</h1>
        <h1 v-else-if="activeTab === 'add'">Add Recipe (Tab)</h1>
        <h1 v-else-if="activeTab === 'list'">List Recipes (Tab)</h1>
        <h1 v-else-if="activeTab === 'settings'">Settings (Tab)</h1>
        <h1 v-else-if="activeTab === 'admin'">Admin View (Tab)</h1>

    </section>

</template>