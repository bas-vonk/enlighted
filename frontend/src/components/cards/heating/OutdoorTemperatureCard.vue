<template>
    <base-card :observedAtTimestamp="currentValueTimestamp">
        <template v-slot:header>Outdoor temperature</template>
        <template v-slot:body>
            <div class="row ps-2">
                <div class="col-4 pe-0 justify-content-center d-flex align-items-center">
                    <spark-line :dataPoints="dataPoints" :dataLabels="dataLabels" />
                </div>
                <div class="col-8 ps-0 justify-content-center display-1"><span>{{ currentValue }}</span><span
                        class="unit px-2">&#176;C</span></div>
            </div>
        </template>
    </base-card>
</template>

<script>
import axios from 'axios'

import BaseCard from '@/components/ui/BaseCard.vue'
import SparkLine from '@/components/ui/charts/SparkLine.vue'

export default {
    name: 'SingleImageCard',
    components: { BaseCard, SparkLine },
    methods: {
        startPolling() {
            this.intervalId = setInterval(this.fetchData, 10000)
        },
        async fetchData() {

            const observedAtLowerBound = Math.floor(Date.now() / 1000) - (60 * 60 * 6)

            const response = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=outdoor_temperature&observed_at_lower_bound=" + observedAtLowerBound)

            this.dataPoints = response.data.data.map(item => item.value).reverse();
            this.dataLabels = response.data.data.map(item => new Date(item.observed_at * 1000).toLocaleString(undefined, {
                month: "numeric", day: "numeric",
                hour: "numeric", minute: "numeric"
            })).reverse();

            this.currentValue = this.dataPoints[this.dataPoints.length - 1];
            this.currentValueTimestamp = this.dataLabels[this.dataLabels.length - 1];

        }
    },
    mounted() {
        this.fetchData()
        this.startPolling();
    },
    data() {
        return {
            dataPoints: null,
            dataLabels: null,
            currentValue: null,
            currentValueTimestamp: null,
        }
    },
}
</script>