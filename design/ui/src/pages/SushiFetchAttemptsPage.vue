<i18n>
en:
    dim:
        report: Report
        organization: Organization
        platform: Platform
    rows: Rows
    columns: Columns
    start_date: Not older than

cs:
    dim:
        report: Report
        organization: Organizace
        platform: Platforma
    rows: Řádky
    columns: Sloupce
    start_date: Ne starší než
</i18n>

<template>
    <v-container>
        <v-row>
            <v-col>
                <v-select
                        :items="xDimensions"
                        v-model="x"
                        :label="$t('columns')"
                ></v-select>
            </v-col>
            <v-col>
                <v-select
                        :items="yDimensions"
                        v-model="y"
                        :label="$t('rows')"
                ></v-select>
            </v-col>
            <v-col>
                <v-menu
                        v-model="dateMenu"
                        :close-on-content-click="false"
                        :nudge-right="40"
                        transition="scale-transition"
                        offset-y
                        full-width
                        min-width="290px"
                >
                    <template v-slot:activator="{ on }">
                        <v-text-field
                                v-model="startDate"
                                :label="$t('start_date')"
                                prepend-icon="fa-calendar"
                                readonly
                                v-on="on"
                                clearable
                        ></v-text-field>
                    </template>
                    <v-date-picker
                            v-model="startDate"
                            @input="dateMenu = false"
                            :allowed-dates="val => val <= (new Date()).toISOString()"
                    >
                    </v-date-picker>
                </v-menu>
            </v-col>
            <v-col cols="auto">
                <v-btn @click="loadAttemptStats()" color="primary">
                    <v-icon small>fa-sync-alt</v-icon>
                </v-btn>
            </v-col>
        </v-row>
        <v-row>
            <v-simple-table dense>
                <thead>
                <tr>
                    <td></td>
                    <th v-for="col in columns" :key="col.pk">{{ col.name }}</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="(row, index) in rows" :key="row.pk">
                    <th>{{ row.name }}</th>
                    <td v-for="(rec, index2) in tableData[index]"
                        :class="rec.total === 0 ? '' : rec.success === 0 ? 'bad' : rec.success === rec.total ? 'great': 'partial'" class="text-center link"
                        @click="showDetails(index2, index)"
                        :key="index + '-' + index2"
                    >
                        {{ rec.total ? rec.success || '-' : ''}}
                        {{ rec.total ? '/' : '' }}
                        {{ rec.total ? rec.failure || '-' : ''}}
                    </td>
                </tr>
                </tbody>
            </v-simple-table>
        </v-row>
        <v-dialog
                v-model="showDetailDialog"
        >
            <SushiAttemptListWidget
                    :organization="selectedItem.organization"
                    :platform="selectedItem.platform"
                    :report="selectedItem.report"
                    :from-date="startDate"
                    @close="showDetailDialog = false"
            >
            </SushiAttemptListWidget>
        </v-dialog>
    </v-container>
</template>

<script>

  import axios from 'axios'
  import {mapActions} from 'vuex'
  import SushiAttemptListWidget from '../components/SushiAttemptListWidget'

  export default {
    name: "SushiFetchAttemptsPage",
    components: {SushiAttemptListWidget},
    data () {
      return {
        statsData: [],
        x: 'report',
        y: 'platform',
        dimensionsRaw: ['organization', 'report', 'platform'],
        columns: [],
        rows: [],
        tableData: {},
        showDetailDialog: false,
        selectedItem: {},
        startDate: null,
        dateMenu: null,
      }
    },
    computed: {
      statsUrl () {
        let base = `/api/sushi-fetch-attempt-stats/?x=${this.x}&y=${this.y}`
        if (this.startDate) {
          base += `&date_from=${this.startDate}`
        }
        return base
      },
      dimensions () {
        return this.dimensionsRaw.map(item => {return {value: item, text: this.$t('dim.'+item)}})
      },
      xDimensions () {
        return this.dimensions
      },
      yDimensions () {
        let x = this.x
        return this.dimensions.filter(item => item.value !== x)
      },
    },
    methods:{
      ...mapActions({
        showSnackbar: 'showSnackbar',
      }),
      async loadAttemptStats () {
        try {
          let response = await axios.get(this.statsUrl)
          this.statsData = response.data
          this.dataToTable()
        } catch (error) {
          this.showSnackbar({content: 'Error fetching SUSHI attempt data: ' + error, color: 'error'})
        }
      },
      dataToTable () {
        let columns = new Set()
        let rows = new Set()
        let col_to_name = {}
        let row_to_name = {}
        for (let rec of this.statsData) {
          let col_id = rec[this.x+'_id']
          let row_id = rec[this.y+'_id']
          columns.add(col_id)
          rows.add(row_id)
          if (!(col_id in col_to_name))
            col_to_name[col_id] = rec[this.x]
          if (!(row_id in row_to_name))
            row_to_name[row_id] = rec[this.y]
        }
        this.columns = [...columns].map(item => {return {name: col_to_name[item], pk: item}})
        this.columns.sort((a, b) => a.name.localeCompare(b.name))
        this.rows = [...rows].map(item => {return {name: row_to_name[item], pk: item}})
        this.rows.sort((a, b) => a.name.localeCompare(b.name))
        // create an empty matrix
        let out = []
        for (let col in this.rows) {
          let rowRec = []
          for (let row in this.columns) {
            rowRec.push({total: 0})
          }
          out.push(rowRec)
        }
        // fill it
        let col_idxs = this.columns.map(item => item.pk)
        let row_idxs = this.rows.map(item => item.pk)
        for (let rec of this.statsData) {
          let x = col_idxs.indexOf(rec[this.x+'_id'])
          let y = row_idxs.indexOf(rec[this.y+'_id'])
          out[y][x] = {
            success: rec.success_count,
            failure: rec.failure_count,
            total: (rec.success_count || 0) + (rec.failure_count || 0)
          }
        }
        this.tableData = out
      },
      showDetails (colIndex, rowIndex) {
        this.selectedItem[this.x] = this.columns[colIndex]
        this.selectedItem[this.y] = this.rows[rowIndex]
        this.showDetailDialog = true
      }
    },
    watch: {
      statsUrl () {
        this.selectedItem = {}
        this.loadAttemptStats()
      },
    },
    mounted() {
      this.loadAttemptStats()
    }

  }
</script>

<style scoped lang="scss">

    td.bad {
        background-color: #eeb3b4;
    }
    td.partial {
        background-color: #f3e2ae;
    }
    td.great {
        background-color: #b7e2b1;
    }
    td.link {
        cursor: pointer;
    }

</style>