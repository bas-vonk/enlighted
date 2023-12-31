<template>
    <base-card :observedAtTimestamp="currentValueTimestamp">
        <template v-slot:header>SPA corr.</template>
        <template v-slot:body>
            <div class="justify-content-center d-flex align-items-center display-1">
                <span>{{ currentValue }}</span><span class="unit px-2"></span>
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

            const response = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=smart_price_adaption_temperature_correction&limit=1")

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