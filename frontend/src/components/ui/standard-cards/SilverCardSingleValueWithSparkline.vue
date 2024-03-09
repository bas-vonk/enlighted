<template>
    <base-card :observedAtTimestamp="currentValueTimestamp">
        <template v-slot:header>{{ title }}</template>
        <template v-slot:body>
            <div class="row ps-2">
                <div class="col-4 pe-0 justify-content-center d-flex align-items-center">
                    <spark-line :dataPoints="dataPoints" :labels="labels" />
                </div>
                <div class="col-8 ps-0 justify-content-center display-1">
                    <span>{{ Math.round(currentValue * 10) / 10 }}</span>
                    <span class="unit px-2" v-html="observationUnit"></span>
                </div>
            </div>
        </template>
    </base-card>
</template>

<script>
import BaseCard from '@/components/ui/BaseCard.vue'
import SparkLine from '@/components/ui/charts/SparkLine.vue'
import { SilverService } from '@/services/silver.js'
import { TimeHelpers, ArrayHelpers } from '@/helpers/helpers.js'

export default {
    name: 'TemperatureOutdoorCard',
    components: { BaseCard, SparkLine },
    props: {
        title: {
            type: String,
            default: false
        },
        deviceName: {
            type: String,
            default: false
        },
        observationName: {
            type: String,
            default: false,
        },
        observationUnit: {
            type: String,
            default: ""
        },
        sparkLineHistoryHours: {
            type: Number,
            default: 12
        }
    },
    methods: {
        startPolling() {
            this.intervalId = setInterval(this.fetchData, 10000)
        },
        async fetchData() {

            let silverService = new SilverService;

            let response = await silverService.get_value_timestamp({
                device_name: this.deviceName,
                observation_name: this.observationName,
                observed_at_lower_bound: Math.floor(Date.now() / 1000) - 3600 * this.sparkLineHistoryHours
            })

            this.dataPoints = response.data.map(item => item.value).reverse();
            this.labels = response.data.map(item => TimeHelpers.getHRFShort(item.observed_at)).reverse();

            this.currentValue = ArrayHelpers.getLastItem(this.dataPoints)
            this.currentValueTimestamp = ArrayHelpers.getLastItem(this.labels)

        }
    },
    mounted() {
        this.fetchData()
        this.startPolling();
    },
    data() {
        return {
            dataPoints: null,
            labels: null,
            currentValue: null,
            currentValueTimestamp: null,
        }
    },
}
</script>