<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

import RecipeCard from '@/components/RecipeCard.vue';
import { useRecipes, type Recipe } from '@/tools/useRecipes';
import { useAuth } from '@/tools/useAuth';
import { useNotifications } from '@/tools/useNotifications';
import { getCurrentContext } from 'vue-router/experimental';

const searchQuery = ref('');
const debouncedQuery = ref('');

const { recipes, loading, error, fetchRecipes, searchRecipes } = useRecipes();
const { currentUser } = useAuth();
const { showToast, showModal } = useNotifications();

onMounted(() => {
    if (!recipes.value.length) {
        fetchRecipes();
    }
});

let timer: number | null = null;

watch(
    searchQuery,
    (value) => {
        if (timer !== null) {
            clearTimeout(timer);
        }
        timer = window.setTimeout(() => {
            debouncedQuery.value = value;
        }, 300);
    }
);

const isAdmin = computed(() => currentUser.value?.role === 'admin');
const currentUserID = computed(() => currentUser.value?.id ?? null);
const publicRecipes = computed(() => recipes.value.filter((r) => r.is_public));

const randomPublicRecipe = computed<Recipe | null>(() => {
    if (!publicRecipes.value.length) return null;
    const idx = Math.floor(Math.random() * publicRecipes.value.length);
    return publicRecipes.value[idx];
});

const searchResults = computed(() => {
    const q = debouncedQuery.value.trim();
    if(!q) return [];

    return(searchRecipes(q));
});

const cardResults = computed(() =>
    searchResults.value.map((r) => {
        const isOwner = currentUserID.value !== null && r.owner_id === currentUserID.value;

        const ownerName = 
        isAdmin.value || isOwner ? r.owner_username : 'Public';

        return {
            id: r.id,
            title: r.title,
            ingredients: r.ingredients,
            instructions: r.instructions,
            ownerName,
            isOwner,
        };
    })
);

const randomCard = computed(() => {
    const r = randomPublicRecipe.value;
    if (!r) return null;

    const isOwner = currentUserID.value !== null && r.owner_id === currentUserID.value;

    const ownerName = isAdmin.value || isOwner ? r.owner_username : 'Public';

    return {
        id: r.id,
        title: r.title,
        instructions: r.instructions,
        ingredients: r.ingredients,
        isOwner,
        ownerName,
    };
});

const { updateRecipe, deleteRecipe } = useRecipes();

function handleModify(id: number) {
    showToast({
        type: 'info',
        message: `Modify from Search not wired to UI yet (id=${id}).`,
    });
}

function handleDelete(id: number) {
    const recipe = recipes.value.find((r) => r.id === id);
    const title = recipe ? recipe.title : `#${id}`;

    showModal({
        type: 'confirm-delete',
        title: 'Delete Recipe',
        message: `Are you sure you want to delete "${title}?" This cannot be undone.." `,
        async onConfirm() {
            const result = await deleteRecipe(id);

            if (!result.ok) {
                showToast({
                    type: 'error',
                    message: result.error ?? 'Failed to delete recipe.',
                });
                return;
            }

            showToast({
                type: 'success',
                message: `Recipe "${title}" deleted.`,
            });
        },
    });
}

</script>

<template> 
    <section>
    <h1>Search View</h1>

    <form @submit.prevent>
        <label for="search-query">Search</label>
        <input id="search-query" type="text" v-model="searchQuery" placeholder="Type to search by title" />
    </form>
    <p v-if="loading">Loading Recipes</p>
    <p v-if="error" style="color: red">{{ error }}</p>
    <div v-if="!loading && !error && !debouncedQuery && randomCard">
        <h2>Random Public Recipe</h2>
        <RecipeCard 
        :id="randomCard.id",
        :title="randomCard.title"
        :ingredients="randomCard.ingredients"
        :instructions="randomCard.instructions"
        :owner-name="randomCard.ownerName"
        :is-owner="randomCard.isOwner"
        :is-admin="isAdmin"
        @modify="handleModify"
        @delete="handleDelete" />
    </div>
    <div v-if="debouncedQuery && !loading && !error" class="recipes-grid">
        <div v-if="cardResults.length === 0">
            No Recipes match "{{ debouncedQuery }}".
        </div>
    <RecipeCard 
        v-for="recipe in cardResults"
        v-else
        :key="recipe.id"
        :id="recipe.id"
        :title="recipe.title"
        :ingredients="recipe.ingredients"
        :instructions="recipe.instructions"
        :owner-name="recipe.ownerName"
        :is-owner="recipe.isOwner"
        :is-admin="isAdmin"
        @modify="handleModify"
        @delete="handleDelete"
    />
    </div>
    
    </section>
</template>