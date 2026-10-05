import { ref, readonly } from 'vue';
import { useApiClient } from './useApiClient';

interface Recipe {
    id: number;
    title: string;
    ingredients: string;
    instructions: string;
    owner_username: string;
    owner_id?: number;
    is_public: boolean;
    user_id?: number;
}

const recipes = ref<Recipe[]>([]);
const selectedRecipe = ref<Recipe | null>(null)
const loading = ref(false);
const error = ref<string | null>(null);

export function useRecipes() {
    const { request } = useApiClient();

    async function fetchRecipes() {
        loading.value = true;
        error.value = null;

        const results = await request<Recipe[]>('/recipes', {
            method: 'GET',
        });

        loading.value = false;

        if (results.error) {
            error.value = results.error;
            return;
        }

        recipes.value = Array.isArray(results.data) ? results.data : [];
    }
    function searchRecipes(query: string): Recipe[] {
        const q = query.trim().toLowerCase();
        if (!q) return recipes.value;
        return recipes.value.filter((r) =>
            r.title?.toLowerCase().includes(q)
        );
    }
    return {
        recipes: readonly(recipes),
        selectedRecipe: readonly(selectedRecipe),
        loading: readonly(loading),
        error: readonly(error),
        fetchRecipes,
        searchRecipes,
    };
}
