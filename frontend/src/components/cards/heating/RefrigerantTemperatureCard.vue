<template>
    <double-value-card :cardTitle="cardTitle" :observedAtTimestamp="observedAtTimestamp" :leftValue="leftValue"
        :leftUnit="leftUnit" :leftExplanation="leftExplanation" :rightValue="rightValue" :rightUnit="rightUnit"
        :rightExplanation="rightExplanation" :isMeasuredReliably="isMeasuredReliably" />
</template>

<script>
import axios from 'axios'

import DoubleValueCard from '@/components/ui/cards/DoubleValueCard.vue'

export default {
    name: 'HeatMediumFluidCard',
    components: { DoubleValueCard },
    data() {
        return {
            cardTitle: "Heat circuit",
            observedAtTimestamp: "",
            leftValue: null,
            leftUnit: "&#176;C",
            leftExplanation: "To house",
            rightValue: null,
            rightUnit: "&#176;C",
            rightExplanation: "From house",
            isMeasuredReliably: true
        }
    },
    methods: {
        startPolling() {
            this.intervalId = setInterval(this.fetchData, 10000)
        },
        async fetchData() {

            // Check the heat circuit pump to see if the data is reliable
            // If the heat circuit pump is not running, the temperature sensors are wandering (and thus unreliable)
            const response_heat_circuit_pump_speed = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=heat_circuit_pump_speed&limit=1")
            if (response_heat_circuit_pump_speed.data.data[0].value === 0) {
                this.isMeasuredReliably = false
            }

            // Fetch data for the supply temperature
            const response_supply = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=heat_medium_flow_temperature&limit=1");
            this.leftValue = response_supply.data.data[0].value;
            this.observedAtTimestamp = new Date(response_supply.data.data[0].observed_at * 1000).toLocaleString(undefined, {
                month: "numeric", day: "numeric",
                hour: "numeric", minute: "numeric"
            })

            // Fetch data for the return temperature
            const response_return = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=heat_medium_flow_return_temperature&limit=1");
            this.rightValue = response_return.data.data[0].value;
        }
    },
    mounted() {
        this.fetchData()
        this.startPolling();
    },
}
</script>
