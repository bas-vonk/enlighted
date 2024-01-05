<template>
    <base-card :observedAtTimestamp="currentValueTimestamp">
        <template v-slot:header>{{ title }}</template>
        <template v-slot:body>
            <div class="justify-content-center d-flex align-items-center display-1">
                <span>{{ currentValue }}</span><span class="unit px-2" v-html="observationUnit"></span>
            </div>
        </template>
    </base-card>
</template>

<script>
import BaseCard from '@/components/ui/BaseCard.vue'
import { SilverService } from '@/services/silver.js'
import { TimeHelpers } from '@/helpers/helpers.js'

export default {
    name: 'SpaSupplyTempCorrectionCard',
    components: { BaseCard },
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
        }
    },
    methods: {
        startPolling() {
            this.intervalId = setInterval(this.fetchData, 60000)
        },
        async fetchData() {

            let silverService = new SilverService()

            let response = await silverService.get_value_timestamp({
                device_name: this.deviceName,
                observation_name: this.observationName,
                limit: 1
            })

            this.currentValue = response.data[0].value
            this.currentValueTimestamp = TimeHelpers.getHRFShort(response.data[0].observed_at)
        }
    },
    mounted() {
        this.fetchData()
        this.startPolling();
    },
    data() {
        return {
            currentValue: null,
            currentValueTimestamp: null
        }
    },
}
</script>