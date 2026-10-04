<script setup lang="ts">

</script>

<template> 
    <section>
        <h1>Add Recipe</h1>

        <form>
            <div>
                <label for="title">
                    Title <span>*</span>
                </label>
                <input id="title" type="text" />
            </div>

            <div>
                <label for="instructions">
                    Instructions
                </label>
                <textarea id="instructions" rows="6">
                </textarea>
            </div>
            
            <div>
                <label for="ingredients">
                    Ingredients <span>*</span>
                </label>
                <textarea id="ingredients" rows="4"></textarea>
            </div>

            <div>
                <label>
                    <input type="checkbox" />
                    Public Recipe
                </label>
            </div>
            <button type="submit">
                Create Recipe
            </button>
        </form>
    </section>
</template>