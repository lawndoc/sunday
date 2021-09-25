<template>
  <q-card>
    <q-card-section class="q-pa-none">
      <!-- eslint-disable vue/no-v-model-argument -->
      <q-table
        title="Meets"
        :rows="data"
        :columns="columns"
        row-key="name"
        :filter="filter"
        :pagination="pagination"
      >
      <!-- eslint-enable -->
        <template v-slot:top-right>
          <q-input v-if="show_filter" filled borderless dense debounce="300" v-model="filter" placeholder="Search">
            <template v-slot:append>
              <q-icon name="search"/>
            </template>
          </q-input>

          <q-btn class="q-ml-sm" icon="filter_list" @click="show_filter=!show_filter" flat/>
        </template>
      </q-table>
    </q-card-section>
  </q-card>
</template>

<script>
import {defineComponent, ref} from 'vue'

const columns = [
  {name: 'date', required:true, align: 'center', label: 'Date', field: 'date', sortable: true},
  {
    name: 'name',
    required: true,
    label: 'Meet',
    align: 'left',
    field: row => row.name,
    format: val => `${val}`,
    sortable: true
  },
  {name: 'location', label: 'Location', field: 'location', sortable: true}
];
const data = [
  {
    name: 'L-S Invite',
    date: '9/13/21',
    location: 'Diamond Trail Golf Course'
  },
  {
    name: 'Oskaloosa Invite',
    date: '9/11/21',
    location: 'Edmunson Park'
  },
];
export default defineComponent({
  name: "MeetsTable",
  setup() {
    const show_filter = ref(false)
    return {
      filter: ref(''),
      show_filter,
      data,
      columns,
      pagination: {
        rowsPerPage: 50
      },
    }
  }
})
</script>

<style scoped>
</style>