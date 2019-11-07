<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <div class="d-flex align-center">
        <v-img
          alt="ModiScript Logo"
          class="shrink mr-2"
          contain
          src="./assets/logo.png"
          transition="scale-transition"
          width="40"
        />
        <h1 class="display-1 font-weight-bold">
          ModiScript
        </h1>
      </div>
    </v-app-bar>

    <v-content>
      <home></home>
    </v-content>
  </v-app>
</template>

<script>
import home from './components/home.vue';

export default {
  name: "App",

  components: {
    home
  },

  data: () => ({
    //
  })
};
</script>
