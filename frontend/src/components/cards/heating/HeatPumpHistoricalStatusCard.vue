<template>
    <base-card :observedAtTimestamp="observedAtTimestamp">
        <template v-slot:header>Historical system status (last 14 days)</template>
        <template v-slot:body>
            <div style="padding: 2rem;">
                <line-chart :labels="labels" :datasets="datasets" />
            </div>
        </template>
    </base-card>
</template>

<script>
import { SilverService } from '@/services/silver.js'
import { TimeHelpers, ArrayHelpers } from '@/helpers/helpers.js'
import BaseCard from '@/components/ui/BaseCard.vue'
import LineChart from '@/components/ui/charts/LineChart.vue'

export default {
    name: 'RecentHistoryCard',
    components: { BaseCard, LineChart },
    methods: {
        startPolling() {
            this.intervalId = setInterval(this.fetchData, 60000)
        },
        async getSystemStatusDatasets() {

            let silverService = new SilverService()

            let response = await silverService.get_value_timestamp({
                device_name: 'f1255pc',
                observation_name: 'system_status',
                observed_at_lower_bound: TimeHelpers.unixDaysInThePast(7)
            })

            let sparseData = ArrayHelpers.makeSparse(response.data, 5)

            return [
                {
                    label: "Inactive",
                    data: sparseData.map((item) => ({
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
                    data: sparseData.map((item) => ({
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
                    data: sparseData.map((item) => ({
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
                    data: sparseData.map((item) => ({
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
                    data: sparseData.map((item) => ({
                        x: item.observed_at.toString(),
                        y: (item.value === 4) ? 1 : 0
                    })),
                    fill: true,
                    backgroundColor: 'rgba(12,109,253, 1)',
                    borderWidth: 0,
                    stepped: true
                }
            ]

        },
        async getOutdoorTemperatureDatasets() {

            let silverService = new SilverService()

            let response = await silverService.get_value_timestamp({
                device_name: 'f1255pc',
                observation_name: 'outdoor_temperature',
                observed_at_lower_bound: TimeHelpers.unixDaysInThePast(7)
            })

            let sparseData = ArrayHelpers.makeSparse(response.data, 300)

            return [
                {
                    label: "Outdoor temperature",
                    data: sparseData.map((item) => ({
                        x: item.observed_at.toString(),
                        y: item.value
                    })),
                    fill: false,
                    borderColor: 'rgb(16,202,240)',
                    borderWidth: 1,
                    tension: 0.3
                }
            ]

        },
        async getAutoModeStopHeatingDataSets() {

            let silverService = new SilverService()

            let response = await silverService.get_value_timestamp({
                device_name: 'f1255pc',
                observation_name: 'auto_mode_stop_heating_temperature',
                observed_at_lower_bound: TimeHelpers.unixDaysInThePast(7)
            })

            let sparseData = ArrayHelpers.makeSparse(response.data, 1)

            return [
                {
                    label: "Auto mode: stop heating",
                    data: sparseData.map((item) => ({
                        x: item.observed_at.toString(),
                        y: item.value
                    })),
                    fill: false,
                    borderColor: 'rgb(242,243,244)',
                    borderWidth: 0.5,
                    stepped: true
                }
            ]

        },
        async fetchData() {

            // Define the datasets
            let systemStatusDatasets = await this.getSystemStatusDatasets()
            let outdoorTemperatureDatasets = await this.getOutdoorTemperatureDatasets()
            let autoModeStopHeatingDataSets = await this.getAutoModeStopHeatingDataSets()

            this.datasets = [
                ...outdoorTemperatureDatasets,
                ...autoModeStopHeatingDataSets,
                ...systemStatusDatasets
            ]

            // Define the labels
            let labels = []
            this.datasets.forEach(dataset => {
                labels.push(...dataset.data.map(item => item.x))
            })
            this.labels = ArrayHelpers.getUniqueItemsSorted(labels)

            // Define observed at timestamp
            this.observedAtTimestamp = TimeHelpers.getHRFShort(ArrayHelpers.getLastItem(this.labels))
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