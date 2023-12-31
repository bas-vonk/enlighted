<template>
    <base-card :observedAtTimestamp="observedAtTimestamp">
        <template v-slot:header>Operating time per price level (%)</template>
        <template v-slot:body>
            <div class="p-3">
                <doughnut-chart :dataPointsPrimaryLabel="dataPointsPrimaryLabel" :dataPointsPrimary="dataPointsPrimary"
                    :dataPointsSecondaryLabel="dataPointsSecondaryLabel" :dataPointsSecondary="dataPointsSecondary"
                    :dataLabels="dataLabels" />
            </div>
        </template>
    </base-card>
</template>

<script>
import axios from 'axios'

import BaseCard from '@/components/ui/BaseCard.vue'
import DoughnutChart from '@/components/ui/charts/DoughnutChart.vue';

export default {
    name: 'SingleImageCard',
    components: { BaseCard, DoughnutChart },
    methods: {
        startPolling() {
            this.intervalId = setInterval(this.fetchData, 10000)
        },
        async fetchData() {

            const response = await axios.get("http://localhost/gold/insight?insight_name=heat_pump_operating_hours_prices");

            this.dataPointsPrimaryLabel = 'Last 7 days'
            this.dataPointsPrimary = Object.values(response.data.insight.last_seven_days)

            this.dataPointsSecondaryLabel = 'Last 60 days'
            this.dataPointsSecondary = Object.values(response.data.insight.last_sixty_days)

            this.dataLabels = Object.keys(response.data.insight.last_seven_days)
            this.observedAtTimestamp = new Date(response.data.observed_at * 1000).toLocaleString(undefined, {
                month: "numeric", day: "numeric",
                hour: "numeric", minute: "numeric"
            })
        }
    },
    mounted() {
        this.fetchData()
        this.startPolling();
    },
    data() {
        return {
            dataPointsPrimaryLabel: '',
            dataPointsPrimary: [],
            dataPointsSecondaryLabel: '',
            dataPointsSecondary: [],
            dataLabels: [],
            observedAtTimestamp: ''
        }
    },
}
</script>