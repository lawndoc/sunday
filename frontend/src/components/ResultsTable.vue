<template>
  <q-card>
    <q-card-section>
      <div class="text-h6 text-grey-8">
        L-S Invite
      </div>
    </q-card-section>
    <q-card-section class="q-pa-none">
      <!-- eslint-disable vue/no-v-model-argument -->
      <q-table
        title="Boys Varsity"
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
          <q-btn
                color="primary"
                icon-right="archive"
                label="Export to csv"
                no-caps
                @click="exportTable"
              />
        </template>
      </q-table>
    </q-card-section>
  </q-card>
</template>

<script>
import {defineComponent, ref} from 'vue'
import {exportFile} from 'quasar'

function wrapCsvValue(val, formatFn) {
  let formatted = formatFn !== void 0
    ? formatFn(val)
    : val
  formatted = formatted === void 0 || formatted === null
    ? ''
    : String(formatted)
  formatted = formatted.split('"').join('""')
  /**
   * Excel accepts \n and \r in strings, but some other CSV parsers do not
   * Uncomment the next two lines to escape new lines
   */
  // .split('\n').join('\\n')
  // .split('\r').join('\\r')
  return `"${formatted}"`
}

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
      columns,
      pagination: {
        rowsPerPage: 50
      },

      exportTable() {
        // naive encoding to csv format
        const content = [columns.map(col => wrapCsvValue(col.label))].concat(
          data.map(row => columns.map(col => wrapCsvValue(
            typeof col.field === 'function'
              ? col.field(row)
              : row[col.field === void 0 ? col.name : col.field],
            col.format
          )).join(','))
        ).join('\r\n')
        const status = exportFile(
          'table-export.csv',
          content,
          'text/csv'
        )
        if (status !== true) {
          $q.notify({
            message: 'Browser denied file download...',
            color: 'negative',
            icon: 'warning'
          })
        }
      }
    }
  }
})
</script>

<style scoped>
</style>