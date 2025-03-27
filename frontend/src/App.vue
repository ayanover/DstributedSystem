<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import NavbarComponent from '@/components/NavbarComponent.vue';
</script>

<template>
  <div>
    <NavbarComponent />
    <main class="container mx-auto py-4">
      <Router-view />
    </main>
  </div>
</template>

<style scoped>

</style>
