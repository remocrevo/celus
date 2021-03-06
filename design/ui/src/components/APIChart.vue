<i18n lang="yaml" src="../locales/common.yaml"></i18n>
<i18n lang="yaml" src="../locales/charts.yaml"></i18n>

<template>
    <LoaderWidget v-if="loading" :height="height" />
    <div v-else-if="dataRaw.length === 0" :style="{'height': height}" id="loading">
        <div>
            <i class="far fa-frown"></i>
            <div class="infotext">{{ $t('chart.no_data') }}</div>
        </div>
    </div>
    <component v-else
            :is="chartComponent"
            :data="chartData"
            :settings="chartSettings"
            :extend="chartExtend"
            :height="height"
            :toolbox="chartToolbox"
            :data-zoom="dataZoom"
            :mark-line="markLine"
            >
    </component>
</template>
<script>
  import VeHistogram from 'v-charts/lib/histogram.common'
  import VeBar from 'v-charts/lib/bar.common'
  import VeLine from 'v-charts/lib/line.common'
  // the following two imports are here to ensure the components at hand will be bundled
  import _dataZoom from 'echarts/lib/component/dataZoom'
  import _toolBox from 'echarts/lib/component/toolbox'
  import axios from 'axios'
  import jsonToPivotjson from 'json-to-pivot-json'
  import { mapActions, mapGetters } from 'vuex'
  import 'echarts/lib/component/markLine'
  import LoaderWidget from './LoaderWidget'

  export default {
    name: 'APIChart',
    components: {VeHistogram, VeBar, VeLine, LoaderWidget},
    props: {
      type: {
        type: String,
        default: 'histogram',
      },
      organization: {
        required: false,
      },
      platform: {
        required: false,
      },
      primaryDimension: {
        required: true,
      },
      secondaryDimension: {
        required: false,
      },
      reportTypeId: {
        required: true,
      },
      metric: {
        required: false,
      },
      title: {  // id of the title to filter on
        type: Number,
        required: false,
      },
      importBatch: {  // id of the Batch
        required: false,
        type: Number,
      },
      dataURLBase: {
        type: String,
        default: '/api/',
      },
      extend: {
        type: Object,
        default: ret => {},
      },
      stack: {
        type: Boolean,
        default: false,
      },
      height: {default: '400px'},
      zoom: {
        type: Boolean,
        default: true,
      },
      ignoreDateRange: {
        type: Boolean,
        default: false,
      },
      orderBy: {},
      showMarkLine: {default: true},
      rawReportType: {
        default: false,
        type: Boolean,
      },
    },
    data () {
      return {
        dataRaw: [],
        data_meta: null,
        loading: true,
      }
    },
    computed: {
      ...mapGetters({
        dateRangeStart: 'dateRangeStartText',
        dateRangeEnd: 'dateRangeEndText',
        selectedOrganization: 'selectedOrganization',
      }),
      dataURL () {
        let reportTypePart = ''  // used do decide if report type should be part of the URL
        if (this.reportTypeId && this.reportTypeId !== -1) {
            reportTypePart = `${this.reportTypeId}/`
        }
        let urlStart = this.rawReportType ? 'chart-data-raw' : 'chart-data'
        let url = `${this.dataURLBase}${urlStart}/${reportTypePart}?prim_dim=${this.primaryDimension}`
        if (!this.ignoreDateRange) {
          url += `&start=${this.dateRangeStart}&end=${this.dateRangeEnd}`
        }
        if (this.secondaryDimension) {
          url += `&sec_dim=${this.secondaryDimension}`
        }
        if (this.platform)
          url += `&platform=${this.platform}`
        if (this.organization)
          url += `&organization=${this.organization}`
        if (this.title)
          url += `&target=${this.title}`
        if (this.importBatch)
          url += `&import_batch=${this.importBatch}`
        return url
      },
      columns () {
        if (this.loading)
          return []
        if (this.dataRaw.length === 0)
          return []
        if (this.secondaryDimension) {
          let rows = this.rows
          return [
            this.dimensionToName(this.primaryDimension),
            ...Object.keys(rows[0]).filter(item => item !== this.primaryDimension)
          ]
        } else {
          return [this.dimensionToName(this.primaryDimension), 'count']
        }
      },
      chartData () {
        return {
            columns: this.columns,
            rows: this.rows,
        }
      },
      chartExtend () {
        let colors = ['#ff0000', '#ff8844', '#ff4488', '#ff4444']
        if (this.primaryDimension === 'organization') {
          let that = this
          return {
            series(item) {
              let organizationRowNum = that.organizationRow
              if (organizationRowNum !== null) {
                let serIdx = 0
                for (let ser of item) {
                  ser.data = ser.data.map((v, index) => ({
                    value: v,
                    itemStyle: {color: index === organizationRowNum ? colors[serIdx % 4] : null}
                  }))
                  serIdx++
                }
              }
              return item
            }
          }
        }
        return {}
      },
      markLine () {
        if (this.primaryDimension === 'organization' && this.showMarkLine && this.organizationRow !== null) {
          return {
            silent: true,
            symbol: ['none', 'none'],
            data: [
              {
                name: 'me',
                yAxis: this.organizationRow,
                lineStyle: {
                  normal: {
                    color: '#aa0010',
                    type: 'solid',
                    width: 1,
                  }
                },
                label: {
                  formatter: this.$t('chart.my_org'),
                  position: 'middle',
                }
              },
            ]
          }
        }
        return {}
      },
      rows () {
        if (this.loading) {
          return []
        }
        // no secondary dimension
        if (this.secondaryDimension) {
          let out = jsonToPivotjson(
            this.dataRaw,
            {
              row: this.primaryDimension,
              column: this.secondaryDimension,
              value: 'count',
            })
          if (this.orderBy) {
            // NOTE: order by sum of values - it does not matter how is the orderBy called
            function sumNonPrimary (rec) {
              // remove value of primary dimension, sum the rest
              return Object.entries(rec).filter(([a, b]) => a !== this.primaryDimension).map(([a, b]) => b).reduce((x, y) => x + y)
            }
            let sum = sumNonPrimary.bind(this)
            out.sort((a, b) => (sum(a) - sum(b)))
          }
          return out
        } else {
          // secondary dimension
          if (this.orderBy) {
            // order by
            this.dataRaw.sort((a, b) => {
              return a[this.orderBy] - b[this.orderBy]
            })
          }
          return this.dataRaw
        }
      },
      organizationRow () {
        if (!this.selectedOrganization) {
          return null
        }
        let i = 0
        for (let row of this.rows) {
          if (row.organization === this.selectedOrganization.name) {
            return i
          }
          i++
        }
        return null
      },
      chartSettings () {
        let out = {}
        if (!this.secondaryDimension) {
          // count is the metric, we remap it to a different name
          out['labelMap'] = {
            'count': this.$i18n.t('chart.count')
          }
        } else {
          if (this.rows && this.rows.length && this.stack) {
            out['stack'] = {
              'all': [...Object.keys(this.rows[0]).filter(item => item !== this.primaryDimension)]
            }
          }
        }
        return out
      },
      chartToolbox () {
        let toolbox = {
          feature: {
            saveAsImage: {
              show: true,
              title: this.$t('chart.toolbox.save_as_image'),
              excludeComponents: ['toolbox', 'dataZoom'],
            },
            myExportData: {
              show: true,
              title: this.$t('chart.toolbox.export_csv'),
              icon: 'path://m 434.57178,114.29929 -83.882,-83.882005 c -9.00169,-9.001761 -21.21063,-14.058933 -33.941,-14.059 H 48.630782 c -26.51,0 -47.9999996,21.49 -47.9999996,48 V 416.35829 c 0,26.51 21.4899996,48 47.9999996,48 H 400.63078 c 26.51,0 48,-21.49 48,-48 v -268.118 c -7e-5,-12.73037 -5.05724,-24.93931 -14.059,-33.941 z m -161.941,-49.941005 v 80.000005 h -128 V 64.358285 Z m -48,152.000005 c -48.523,0 -88,39.477 -88,88 0,48.523 39.477,88 88,88 48.523,0 88,-39.477 88,-88 0,-48.523 -39.477,-88 -88,-88 z',
              onclick: function (that) {
                return function () {
                  window.open(that.dataURL + '&format=csv')
                }
              }(this)
            }
          }
        }
        if (this.zoom && false) {  // temporarily disabled, there is bug in echarts - https://github.com/apache/incubator-echarts/issues/10972
          toolbox.feature['dataZoom'] = {
              show : true,
              title : {
                zoom : this.$t('chart.toolbox.zoom'),
                back : this.$t('chart.toolbox.zoom_back'),
              }
          }
        }
        return toolbox
      },
      dataZoom () {
        if (this.zoom) {
          return [
            {
              type: 'slider',
              start: 0,
              end: 100,
              yAxisIndex: this.type === 'bar' ? 0 : null,
            },
          ]
        } else {
          return []
        }
      },
      chartComponent () {
        if (this.type === 'bar') {
          return VeBar
        } else if (this.type === 'histogram') {
          return VeHistogram
        } else {
          return VeLine
        }
      }
    },
    methods: {
      ...mapActions({
        showSnackbar: 'showSnackbar',
      }),
      async loadData() {
        this.loading = true
        this.dataRaw = []
        if (this.dataURL) {
          try {
            let response = await axios.get(this.dataURL)
            // reformat date value to exclude the day component
            this.dataRaw = response.data.data.map(dict => {if ('date' in dict) dict['date'] = dict.date.substring(0, 7); return dict})
          } catch (error) {
            this.showSnackbar({content: 'Error fetching data: '+error})
          } finally {
            this.loading = false
          }
        }
      },
      dimensionToName (dim) {
        if (typeof dim === 'number') {
          return 'dim' + dim
        }
        return dim
      }
    },
    mounted () {
      this.loadData()
    },
    watch: {
      dataURL () {
        this.loadData()
      },
    }
  }
</script>
<style scoped lang="scss">

    .accomp-text {
        font-size: 125%;
        text-align: center;

        &.left {
            padding-right: 0;
        }
        &.right {
            padding-left: 0;
        }

    }

    .chart {
        margin: 1rem;
    }

    #loading {
        font-size: 60px;
        color: #1db79a88;
        text-align: center;

        i {
            margin-top: 160px;
        }

        div.infotext {
            font-size: 26px;
        }
    }

</style>
