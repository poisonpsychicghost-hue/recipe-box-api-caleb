<script setup lang="ts">
const props = defineProps<{
    id: number;
    title: string;
    ingredients: string;
    instructions: string;
    owner_id?: number;
    ownerName: string;
    isOwner: boolean;
    isAdmin: boolean;
}>();

const emit = defineEmits<{
    modify: [id: number];
    delete: [id: number];
}>();

function handleModify() {
    emit('modify', props.id)
}

function handleDelete() {
    emit('delete', props.id);
}

</script>


<template> 
    <article class="recipe-card">
        <!-- default logo / placeholder-->
         <div class="recipe-card__logo">
            <span>RB</span>
         </div>

         <header class="recipe-card__header">
            <h2>{{ title }}</h2>
         </header>

         <section class="recipe-card__body">
            <div class="recipe-card_column recipe-card__column--instructions">
                <h3>Instructions</h3>
                <div class="recipe=card__scroll">
                    <p>{{ instructions }}</p>
                </div>
            </div>
            
            <div class="recipe-card__column recipe-card__column--ingredients">
                <h3>Ingredients</h3>
                <div class="recipe-card__scroll">
                    <p>{{ ingredients }}</p>
                </div>
            </div>
         </section>

         <footer class="recipe-card__footer">
            <div v-if="(isOwner || isAdmin) && ownerName" class="recipe-card__owner">
                Owner: {{ ownerName }}
            </div>

            <div class="recipe-card__actions">
                <button
                    v-if="isOwner || isAdmin"
                    type="button"
                    @click="handleModify">
                    Modify
                </button>

                <button
                    v-if="isOwner || isAdmin"
                    type="button"
                    @click="handleDelete">
                    Delete
                </button>
            </div>
         </footer>
    </article>
</template>