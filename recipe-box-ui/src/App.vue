<script setup lang="ts">
import TopNav from './components/TopNav.vue'
import FooterBar from './components/FooterBar.vue';


</script>

<template>
  <TopNav />
  <main>
  <router-view />
  </main>
  <FooterBar />

</template>

<style scoped></style>
