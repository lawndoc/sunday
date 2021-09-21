<template>
  <q-page class="q-pa-sm">

    <results-table/>

  </q-page>
</template>

<script>
import {defineComponent, defineAsyncComponent} from 'vue';
export default defineComponent({
  name: "Tables",
  components: {
    ResultsTable: defineAsyncComponent(() => import('components/ResultsTable'))
  },
})
</script>

<style>
</style>