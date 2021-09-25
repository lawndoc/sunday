<template>
  <q-page class="q-pa-sm">

    <meets-table/>

  </q-page>
</template>

<script>
import {defineComponent, defineAsyncComponent} from 'vue';
export default defineComponent({
  name: "Table",
  components: {
    MeetsTable: defineAsyncComponent(() => import('components/MeetsTable'))
  },
})
</script>

<style>
</style>