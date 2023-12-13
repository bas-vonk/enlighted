<script setup>
import { RouterView } from 'vue-router'
import TheSidebar from '@/components/ui/TheSidebar.vue'
import TheHeader from '@/components/ui/TheHeader.vue'

</script>

<template>
  <TheHeader />
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-auto bg-dark sticky-top">
        <TheSidebar />
      </div>
      <div class="col-sm p-3 min-vh-100">
        <RouterView />
      </div>
    </div>
  </div>
</template>

<style></style>
