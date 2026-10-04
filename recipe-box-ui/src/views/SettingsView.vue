<script setup lang="ts">

</script>

<template> 
    <section>
        <h1>Settings</h1>

        <div>
            <label>
                <input type="checkbox" />
                Dark Mode
            </label>
        </div>

        <div>
            <label for="font-size">
                Font Size
            </label>
            <input id="font-size" type="range" min="0.9" max="1.25" step="0.05" />
        </div>

        <div>
            <label>
                <input type="checkbox" />
                Dyslexic-Friendly Font
            </label>
        </div>

    </section>
</template>