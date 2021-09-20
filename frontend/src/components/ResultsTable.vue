<template>
  <q-card>
    <q-card-section>
      <div class="text-h6 text-grey-8">
        L-S Invite
      </div>
    </q-card-section>
    <q-card-section class="q-pa-none">
      <q-table
        title="Boys Varsity"
        :rows="data"
        :columns="columns"
        row-key="name"
        :filter="filter"
      >
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
  {
    name: 'name',
    required: true,
    label: 'Athlete',
    align: 'left',
    field: row => row.name,
    format: val => `${val}`,
    sortable: true
  },
  {name: 'year', align: 'center', label: 'Year', field: 'year', sortable: true},
  {name: 'school', label: 'School', field: 'school', sortable: true},
  {name: 'time', label: 'Time', field: 'time', sortable: true}
];
const data = [
  {
    name: 'Ryan Natelborg',
    year: 2024,
    school: 'Pella Christian',
    time: '18:35'
  },
  {
    name: 'Danny Andringa',
    year: 2022,
    school: 'Pella Christian',
    time: '18:46'
  },
  {
    name: 'Kaden Van Wyngarden',
    year: 2023,
    school: 'Pella Christian',
    time: '18:03'
  },
  {
    name: 'Brant Vander Hart',
    year: 2022,
    school: 'Pella Christian',
    time: '18:55'
  },
  {
    name: 'Tysen DeVries',
    year: 2024,
    school: 'Pella Christian',
    time: '19:22'
  },
  {
    name: 'Ben Gosselink',
    year: 2023,
    school: 'Pella Christian',
    time: '19:40'
  },
  {
    name: 'C.J. May',
    year: 2016,
    school: 'Aplington Parkersburg',
    time: '15:14'
  },
];
export default defineComponent({
  name: "ResultsTable",
  setup() {
    const show_filter = ref(false)
    return {
      filter: ref(''),
      show_filter,
      data,
      columns
    }
  }
})
</script>

<style scoped>
</style>