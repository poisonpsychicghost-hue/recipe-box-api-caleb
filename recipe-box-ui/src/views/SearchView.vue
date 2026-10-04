<script setup lang="ts">
import { ref } from 'vue'
import RecipeCard from '@/components/RecipeCard.vue';

</script>

<template> 
    <section>
    <h1>Search View</h1>

    <form>
        <label for="search-query">Search</label>
        <input id="search-query" type="text" />
        <button type="button">
            Search
        </button>
    </form>

    <div>
    <RecipeCard />
    </div>
    
    </section>
</template>