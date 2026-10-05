<script setup lang="ts">
import RecipeCard from '@/components/RecipeCard.vue';

const recipes = [
    {
        id: 1,
        title: 'Test Recipe',
        ingredients: 'eggs',
        instructions: 'scramble',
        ownerName: 'DEV123',
        isOwner: true,
    },
    {
        id: 2,
        title: "Test 2",
        ingredients: 'Egg Flour water',
        instructions: 'Mix, Bake, Eat',
        ownerName: 'Carlos',
        isOwner: false,
    },
];

const isAdmin = true

function handleModify(id: number) {
    console.log('modify Clicked for', id);

}

function handleDelete(id: number) {
    console.log('Delete called for', id)
}

</script>

<template> 
    <section>
        <h1>List Recipes</h1>

        <div>
            <RecipeCard 
                v-for="recipe in recipes"
                :key="recipe.id"
                :id="recipe.id"
                :title="recipe.title"
                :ingredients="recipe.ingredients"
                :instructions="recipe.instructions"
                :is-owner="recipe.isOwner"
                :is-admin="isAdmin"
                @modify="handleModify"
                @delete="handleDelete"
                />
        </div>

    </section>
</template>