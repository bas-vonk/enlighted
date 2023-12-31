<template>
    <base-card :observedAtTimestamp="observedAtTimestamp">
        <template v-slot:header>Historical indoor and outdoor temperature</template>
        <template v-slot:body>
            <div style="padding: 2rem;"><line-chart :labels="labels" :datasets="datasets"
                    :observedAtTimestamp="observedAtTimestamp" /></div>
        </template>
    </base-card>
</template>

<script>
import axios from 'axios'

import BaseCard from '@/components/ui/BaseCard.vue'
import LineChart from '@/components/ui/charts/LineChart.vue'

export default {
    name: 'RecentHistoryCard',
    components: { BaseCard, LineChart },
    methods: {
        startPolling() {
            this.intervalId = setInterval(this.fetchData, 60000)
        },
        async fetchData() {

            const observedAtLowerBound = Math.floor(Date.now() / 1000) - (60 * 60 * 24 * 60)

            const response_1 = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=room_temperature&observed_at_lower_bound=" + observedAtLowerBound)
            const response_2 = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=outdoor_temperature_avg&observed_at_lower_bound=" + observedAtLowerBound)

            // make data sparse
            let data_1 = response_1.data.data.filter((item, index) => index % 300 === 0)
            let data_2 = response_2.data.data.filter((item, index) => index % 300 === 0)

            this.datasets = [
                {
                    label: response_1.data.observation_name,
                    data: data_1.map((item) => ({
                        x: item.observed_at.toString(),
                        y: item.value
                    })),
                    indexAxis: 'x',
                    borderColor: 'rgb(214,51,132)',
                    borderWidth: 1,
                    tension: 0.3
                },
                {
                    label: response_2.data.observation_name,
                    data: data_2.map((item) => ({
                        x: item.observed_at.toString(),
                        y: item.value
                    })),
                    indexAxis: 'x',
                    borderColor: 'rgb(16,202,240)',
                    borderWidth: 1,
                    tension: 0.3
                }
            ]

            let labels = []
            this.datasets.forEach(dataset => {
                labels.push(...dataset.data.map(item => item.x))
            })
            this.labels = [...new Set(labels)].sort()

        }
    },
    mounted() {
        this.fetchData()
        this.startPolling();
    },
    data() {
        return {
            datasets: [],
            labels: [],
            observedAtTimestamp: ""
        }
    },
}
</script>