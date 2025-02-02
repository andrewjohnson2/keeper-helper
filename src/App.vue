<script setup>
import { RouterLink, RouterView } from "vue-router";
import { onMounted, reactive } from "vue";
import { init } from "./team";


onMounted(() => {
  init();
});
</script>

<template>
  <RouterView />
</template>

<style scoped></style>
