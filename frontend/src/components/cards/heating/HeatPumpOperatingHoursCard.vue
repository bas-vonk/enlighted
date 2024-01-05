<template>
    <base-card :observedAtTimestamp="observedAtTimestamp">
        <template v-slot:header>Operating time per price level (%)</template>
        <template v-slot:body>
            <div class="p-3">
                <doughnut-chart :labels="labels" :datasets="datasets" />
            </div>
        </template>
    </base-card>
</template>

<script>

import { GoldService } from '@/services/gold.js'
import { TimeHelpers } from '@/helpers/helpers.js'
import BaseCard from '@/components/ui/BaseCard.vue'
import DoughnutChart from '@/components/ui/charts/DoughnutChart.vue';

export default {
    name: 'SingleImageCard',
    components: { BaseCard, DoughnutChart },
    methods: {
        startPolling() {
            this.intervalId = setInterval(this.fetchData, 60000)
        },
        async fetchData() {

            let goldService = new GoldService()

            let response = await goldService.get_insight({
                insight_name: "heat_pump_operating_hours_prices"
            })

            this.observedAtTimestamp = TimeHelpers.getHRFShort(response.observed_at)
            this.labels = Object.keys(response.insight.last_seven_days)
            this.datasets = [
                {
                    label: 'Last 7 days',
                    backgroundColor: this.labels.map(label => this.colorPerLabel[label]),
                    data: Object.values(response.insight.last_seven_days),
                    borderWidth: 5,
                    borderColor: "rgb(52, 58, 63)"
                },
                {
                    label: 'Last 60 days',
                    backgroundColor: this.labels.map(label => this.colorPerLabel[label]),
                    data: Object.values(response.insight.last_sixty_days),
                    borderWidth: 5,
                    borderColor: "rgb(52, 58, 63)"
                }

            ]

        }
    },
    mounted() {
        this.fetchData()
        this.startPolling();
    },
    data() {
        return {
            colorPerLabel: {
                Cheap: '#10CAF0',
                Average: '#6F42C1',
                Expensive: '#D63384'
            },
            datasets: [],
            labels: [],
            observedAtTimestamp: ''
        }
    },
}
</script>