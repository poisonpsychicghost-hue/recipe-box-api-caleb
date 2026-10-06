<script setup lang="ts">
import { computed } from 'vue';
import { useTheme } from '@/tools/useTheme';

const {
    isDarkMode, fontSizeScale, dyslexicFriendlyEnabled, toggleDarkmode, setDyslexicFriendly, setFontSizeScale
} = useTheme()

const fontScaleInput = computed({
    get() {
        return fontSizeScale.value;
    },
    set(value: number) {
        setFontSizeScale(value)
    }
});

</script>

<template> 
    <section>
        <h1>Settings</h1>

        <div>
            <label>
                <input type="checkbox" :checked="isDarkMode" @change="toggleDarkmode" />
                Dark Mode
            </label>
        </div>

        <div>
            <label for="font-size-range">
                Font Size ({{ fontScaleInput.toFixed(2) }})
            </label>
            <input id="font-size" type="range" min="0.9" max="1.25" step="0.05" v-model.number="fontScaleInput" />
        </div>

        <div>
            <label>
                <input type="checkbox" :checked="dyslexicFriendlyEnabled" @change="setDyslexicFriendly" />
                Dyslexic-Friendly Font
            </label>
        </div>

    </section>
</template>