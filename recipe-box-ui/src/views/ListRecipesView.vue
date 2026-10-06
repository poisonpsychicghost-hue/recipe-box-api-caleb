<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

import RecipeCard from '@/components/RecipeCard.vue';
import { useRecipes } from '@/tools/useRecipes';
import { useAuth } from '@/tools/useAuth';
import { useNotifications } from '@/tools/useNotifications';

const { recipes, loading, error, fetchRecipes, updateRecipe } = useRecipes();
const { currentUser } = useAuth();
const { showToast, showModal } = useNotifications();

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

const isEditOpen = ref(false);
const editId = ref<number | null>(null);
const editTitle = ref('');
const editIngredients = ref('');
const editInstructions = ref('');
const editIsPublic = ref(true);
const editError = ref<string | null>(null);

function openEdit(id: number) {
  const recipe = recipes.value.find((r) => r.id === id);
  if (!recipe) return;

  editId.value = id;
  editTitle.value = recipe.title;
  editIngredients.value = recipe.ingredients;
  editInstructions.value = recipe.instructions;
  editIsPublic.value = recipe.is_public;
  editError.value = null;
  isEditOpen.value = true;
}

function closeEdit() {
  isEditOpen.value = false;
  editId.value = null;
  editError.value = null;
}

async function saveEdit(e: Event) {
  e.preventDefault();
  if (editId.value === null) return;

  if (!editTitle.value || !editIngredients.value ) {
    editError.value = 'Title and Ingredients are required.';
    return;
  }
  const result = await updateRecipe(editId.value, {
    title: editTitle.value,
    ingredients: editIngredients.value,
    instructions: editInstructions.value,
    is_public: editIsPublic.value,
  });

  if (!result.ok) {
    editError.value = result.error ?? 'Update failed';
    return;
  }

  showToast({ type: 'success', message: 'Recipe updated.' });
  isEditOpen.value = false;
}


function handleModify(id: number) {
  openEdit(id);

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

    <div v-if="isEditOpen" class="modal-backdrop">
      <div class="modal">
        <h2>Edit Recipe</h2>

        <form @submit="saveEdit">
          <div>
            <label for="edit-title">Title</label>
            <input id="edit-title" v-model="editTitle" />
          </div>
          <div>
            <label for="edit-ingredients">Ingredients</label>
            <textarea id="edit-ingredients" v-model="editIngredients" />
          </div>
          <div>
            <label for="edit-instructions">Instructions</label>
            <textarea id="edit-instructions" v-model="editInstructions" />
          </div>
          <div>
            <label><input type="checkbox" v-model="editIsPublic" />Public</label>
          </div>

          <p v-if="editError" style="color: red;">{{ editError }}</p>

          <div>
            <button type="submit">Save</button>
            <button type="button" @click="closeEdit">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

<style>
@import '../styles/base.css'
</style>
