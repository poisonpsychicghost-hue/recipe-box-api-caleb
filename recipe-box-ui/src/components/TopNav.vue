<script setup lang="ts">
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

</script>

<template>
    <header> 
        <span>Sirius Recipes</span>
        <nav>
            <button
                v-for="tab in tabs"
                :key="tab.key"
                type="button"
                @click="emit('change-tab', tab.key)"
            >
                {{ tab.label }}
        </button>
        </nav>
        <span>FakeUsername</span>
        <span>User</span>
    </header>
</template>