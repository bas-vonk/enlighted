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
import BaseCard from '@/components/ui/BaseCard.vue'
import LineChart from '@/components/ui/charts/LineChart.vue'
import { SilverService } from '@/services/silver.js'
import { TimeHelpers, ArrayHelpers } from '@/helpers/helpers.js'

export default {
    name: 'RecentHistoryCard',
    components: { BaseCard, LineChart },
    methods: {
        startPolling() {
            this.intervalId = setInterval(this.fetchData, 60000)
        },

        async getIndoorTemperatureDataset() {

            let silverService = new SilverService()

            let response = await silverService.get_value_timestamp({
                device_name: 'f1255pc',
                observation_name: 'room_temperature',
                observed_at_lower_bound: TimeHelpers.unixDaysInThePast(7)
            })

            let sparseData = ArrayHelpers.makeSparse(response.data, 60)

            return {
                label: "Indoor temp.",
                data: sparseData.map((item) => ({
                    x: item.observed_at.toString(),
                    y: item.value
                })),
                borderColor: 'rgb(214,51,132)',
                borderWidth: 1,
                tension: 0.3
            }

        },
        async getOutdoorTemperatureDataset() {

            let silverService = new SilverService()

            let response = await silverService.get_value_timestamp({
                device_name: 'f1255pc',
                observation_name: 'outdoor_temperature',
                observed_at_lower_bound: TimeHelpers.unixDaysInThePast(7)
            })

            let sparseData = ArrayHelpers.makeSparse(response.data, 300)

            return {
                label: "Outdoor temp.",
                data: sparseData.map((item) => ({
                    x: item.observed_at.toString(),
                    y: item.value
                })),
                borderColor: 'rgb(16,202,240)',
                borderWidth: 1,
                tension: 0.3
            }

        },
        async fetchData() {

            // Define the datasets
            let indoorTemperatureDataset = await this.getIndoorTemperatureDataset()
            let outdoorTemperatureDataset = await this.getOutdoorTemperatureDataset()

            this.datasets = [
                indoorTemperatureDataset,
                outdoorTemperatureDataset
            ]

            // Define the labels
            let labels = []
            this.datasets.forEach(dataset => {
                labels.push(...dataset.data.map(item => item.x))
            })
            this.labels = ArrayHelpers.getUniqueItemsSorted(labels)

            // Define observed at timestamp
            this.observedAtTimestamp = TimeHelpers.getHRFShort(ArrayHelpers.getLastItem(labels))
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