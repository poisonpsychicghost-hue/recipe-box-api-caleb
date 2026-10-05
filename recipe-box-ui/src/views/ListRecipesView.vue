<script setup lang="ts">
import { onMounted, computed } from 'vue'

import RecipeCard from '@/components/RecipeCard.vue';
import { useRecipes } from '@/tools/useRecipes';
import { useAuth } from '@/tools/useAuth';

const { recipes, loading, error, fetchRecipes } = useRecipes();
const { currentUser } = useAuth();

onMounted(() => {fetchRecipes();});

const isAdmin = computed(() => currentUser.value?.role === 'admin');
const currentUserId = computed(() => currentUser.value?.id);

const cardRecipes = computed(() =>
    recipes.value.map((r) => {
      const isOwner = 
      currentUserId.value !== null &&
      r.owner_id === currentUserId.value;

      const ownerName = isAdmin.value || isOwner ? r.owner_username : 'Public';

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


function handleModify(id: number) {
    console.log('modify Clicked for', id);

}

function handleDelete(id: number) {
    console.log('Delete called for', id)
}

</script>

<template>
  <section>
    <h1>All Recipes</h1>

    <p v-if="loading">Loading recipes…</p>
    <p v-if="error" style="color: red;">{{ error }}</p>

    <div
      v-if="!loading && !error && cardRecipes.length === 0"
    >
      No recipes found.
    </div>

    <div
      v-if="cardRecipes.length > 0"
      class="recipes-grid"
    >
      <RecipeCard
        v-for="recipe in cardRecipes"
        :key="recipe.id"
        :id="recipe.id"
        :title="recipe.title"
        :ingredients="recipe.ingredients"
        :instructions="recipe.instructions"
        :ownerName="recipe.ownerName"
        :is-owner="recipe.isOwner"
        :is-admin="isAdmin"
        @modify="handleModify"
        @delete="handleDelete"
      />
    </div>
  </section>
</template>


