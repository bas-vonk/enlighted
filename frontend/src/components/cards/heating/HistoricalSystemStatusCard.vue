<template>
    <base-card :observedAtTimestamp="observedAtTimestamp">
        <template v-slot:header>Historical system status (last 14 days)</template>
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

            // Get the data
            const observedAtLowerBound = Math.floor(Date.now() / 1000) - (60 * 60 * 24 * 14)
            const response_system_status = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=system_status&observed_at_lower_bound=" + observedAtLowerBound)
            const response_outdoor_temperature = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=outdoor_temperature_avg&observed_at_lower_bound=" + observedAtLowerBound)
            const response_auto_mode_stop_heating = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=auto_mode_stop_heating_temperature&observed_at_lower_bound=" + observedAtLowerBound)

            // make data sparse
            let data_system_status = response_system_status.data.data.filter((item, index) => index % 5 === 0)
            let data_outdoor_temperature = response_outdoor_temperature.data.data.filter((item, index) => index % 300 === 0)
            let data_auto_mode_stop_heating = response_auto_mode_stop_heating.data.data.filter((item, index) => index % 1 === 0)

            this.datasets = [
                {
                    label: "Inactive",
                    data: data_system_status.map((item) => ({
                        x: item.observed_at.toString(),
                        y: (item.value === 0) ? 1 : 0
                    })),
                    fill: true,
                    backgroundColor: 'rgb(52, 58, 63, 1)',
                    borderWidth: 0,
                    stepped: true
                },
                {
                    label: "Hot Water",
                    data: data_system_status.map((item) => ({
                        x: item.observed_at.toString(),
                        y: (item.value === 1) ? 1 : 0
                    })),
                    fill: true,
                    backgroundColor: 'rgb(111,66,193, 1)',
                    borderWidth: 0,
                    stepped: true
                },
                {
                    label: "Heating",
                    data: data_system_status.map((item) => ({
                        x: item.observed_at.toString(),
                        y: (item.value === 2) ? 1 : 0
                    })),
                    fill: true,
                    backgroundColor: 'rgba(214,51,132, 1)',
                    borderWidth: 0,
                    stepped: true
                },
                {
                    label: "Circulation",
                    data: data_system_status.map((item) => ({
                        x: item.observed_at.toString(),
                        y: (item.value === 3) ? 1 : 0
                    })),
                    fill: true,
                    backgroundColor: 'rgba(253,126,19, 1)',
                    borderWidth: 0,
                    stepped: true
                },
                {
                    label: "Cooling",
                    data: data_system_status.map((item) => ({
                        x: item.observed_at.toString(),
                        y: (item.value === 4) ? 1 : 0
                    })),
                    fill: true,
                    backgroundColor: 'rgba(12,109,253, 1)',
                    borderWidth: 0,
                    stepped: true
                },
                {
                    label: "Outdoor temperature",
                    data: data_outdoor_temperature.map((item) => ({
                        x: item.observed_at.toString(),
                        y: item.value
                    })),
                    borderColor: 'rgb(255,255,255)',
                    borderWidth: 1,
                    tension: 0.3
                },
                {
                    label: "Auto mode: stop heating",
                    data: data_auto_mode_stop_heating.map((item) => ({
                        x: item.observed_at.toString(),
                        y: item.value
                    })),
                    borderColor: 'rgb(120,120,120)',
                    borderWidth: 1,
                    stepped: true
                }
            ]
            let labels = []
            this.datasets.forEach(dataset => {
                labels.push(...dataset.data.map(item => item.x))
            })
            this.labels = [...new Set(labels)].sort()
            this.observedAtTimestamp = new Date(this.labels[this.labels.length - 1] * 1000).toLocaleString(undefined, {
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
            labels: [],
            datasets: [],
            observedAtTimestamp: ""
        }
    },
}
</script>