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

<style lang="scss">
@import "../node_modules/bootstrap/scss/bootstrap";
@import url(https://db.onlinewebfonts.com/c/22db60d19480ba0274c9eb6ba877ea9b?family=Aharoni+Bold+V1);

.container-fluid {
  background-color: $gray-900 !important;
}

.unit {
  font-size: 2rem !important;
  color: white !important;
}

.icon-blue {
  fill: $blue;
}

.icon-orange {
  fill: $orange
}

.icon-purple {
  fill: $purple;
}

.icon-pink {
  fill: $pink;
}

.icon-cyan {
  fill: $cyan;
}

.icon-inactive {
  fill: $white;
  opacity: 10%;
}
</style>
