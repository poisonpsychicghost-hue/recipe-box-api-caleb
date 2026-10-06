<script setup lang="ts">
import { ref } from 'vue';
import { useRecipes } from '@/tools/useRecipes';
import { useNotifications } from '@/tools/useNotifications';

const title = ref('');
const ingredients = ref('');
const instructions = ref('');
const isPublic = ref(true);

const isSubmitting = ref(false);
const localError = ref<string | null>(null);

const { createRecipe } = useRecipes();
const { showToast } = useNotifications();

async function handleSubmit(e: Event) {
    e.preventDefault();
    localError.value = null;

    if (!title.value.trim() || !ingredients.value.trim()) {
        localError.value = 'Title and Ingredients are required.';
        return;
    }

    isSubmitting.value = true;

    const result = await createRecipe({
        title: title.value.trim(),
        ingredients: ingredients.value.trim(),
        instructions: instructions.value.trim(),
        is_public: isPublic.value,
    });

    isSubmitting.value = false;

    if (!result.ok) {
        localError.value = result.error ?? 'Failed to create recipe.';
        return;
    }

    title.value = '';
    ingredients.value = '';
    instructions.value = '';
    isPublic.value = true;

    showToast({
        type: 'success',
        message: `Recipe "${result.recipe?.title}" added.`,
    });
}

</script>

<template> 
    <section>
        <h1>Add Recipe</h1>

        <form @submit="handleSubmit">
            <div>
                <label for="title">
                    Title <span>*</span>
                </label>
                <input id="title" v-model="title" />
            </div>
            
            <div>
                <label for="ingredients">
                    Ingredients <span>*</span>
                </label>
                <textarea id="ingredients" v-model="ingredients" rows="4"></textarea>
            </div>

            <div>
                <label for="instructions">
                    Instructions
                </label>
                <textarea id="instructions" v-model="instructions" rows="6">
                </textarea>
            </div>

            <div>
                <label>
                    <input type="checkbox" v-model="isPublic" />
                    Public Recipe
                </label>
            </div>

            <p v-if="localError" style="color: red;">{{ localError }}</p>

            <button type="submit" :disabled="isSubmitting">
                {{ isSubmitting ? 'Creating...' : 'Create Recipe' }}
            </button>
        </form>
    </section>
</template>