<template>
    <base-card :observedAtTimestamp="observedAtTimestamp">
        <template v-slot:header>Heat pump status</template>
        <template v-slot:body>
            <div class="row px-4">
                <div class="col p-0 d-flex justify-content-left align-items-end">
                    <compressor-icon :class="{ 'icon-orange': compressorIsActive, 'icon-inactive': !compressorIsActive }"
                        class="icon-small p-1">
                    </compressor-icon>
                </div>
                <div class="col p-0 d-flex justify-content-left align-items-end">
                    <heat-circuit-pump-icon
                        :class="{ 'icon-orange': heatCircuitPumpIsActive, 'icon-inactive': !heatCircuitPumpIsActive }"
                        class="icon-small p-1">
                    </heat-circuit-pump-icon>
                </div>
                <div class="col p-0 d-flex justify-content-left align-items-end">
                    <brine-circuit-pump-icon
                        :class="{ 'icon-orange': brineCircuitPumpIsActive, 'icon-inactive': !brineCircuitPumpIsActive }"
                        class="icon-small p-1">
                    </brine-circuit-pump-icon>
                </div>
                <div class="col-4 p-0 circle square d-flex justify-content-center align-items-center">
                    <cooling-icon v-if="coolingIsActive" class="icon-large icon-blue" />
                    <heating-house-icon v-else-if="heatingHouseIsActive" class=" icon-large icon-pink" />
                    <heating-water-icon v-else-if="heatingWaterIsActive" class="icon-large icon-purple" />
                    <sleep-icon v-else class="icon-large" />
                </div>
            </div>
        </template>
    </base-card>
</template>

<script>
import { SilverService } from '@/services/silver.js'
import { TimeHelpers } from '@/helpers/helpers.js'
import BaseCard from '@/components/ui/BaseCard.vue'

import BrineCircuitPumpIcon from '@/components/icons/BrineCircuitPumpIcon.vue'
import HeatCircuitPumpIcon from '@/components/icons/HeatCircuitPumpIcon.vue'
import CompressorIcon from '@/components/icons/CompressorIcon.vue'
import SleepIcon from '@/components/icons/SleepIcon.vue'
import CoolingIcon from '@/components/icons/CoolingIcon.vue'
import HeatingHouseIcon from '@/components/icons/HeatingHouseIcon.vue'
import HeatingWaterIcon from '@/components/icons/HeatingWaterIcon.vue'


export default {
    name: 'SingleImageCard',
    components: {
        BaseCard,
        BrineCircuitPumpIcon,
        HeatCircuitPumpIcon,
        CompressorIcon,
        SleepIcon,
        CoolingIcon,
        HeatingHouseIcon,
        HeatingWaterIcon
    },
    methods: {
        startPolling() {
            this.intervalId = setInterval(this.updateStatus, 60000)
        },
        resetFunctionStatus() {
            this.coolingIsActive = false;
            this.heatingHouseIsActive = false;
            this.heatingWaterIsActive = false;
        },
        async setFunctionStatus() {
            let silverService = new SilverService()

            let response = await silverService.get_value_timestamp({
                device_name: 'f1255pc',
                observation_name: 'system_status',
                limit: 1
            })

            this.observedAtTimestamp = TimeHelpers.getHRFShort(response.data[0].observed_at)

            this.resetFunctionStatus()
            if (response.data[0]['value'] === 1) {
                this.heatingWaterIsActive = true;
            } else if (response.data[0]['value'] === 2) {
                this.heatingHouseIsActive = true;
            } else if (response.data[0]['value'] === 4) {
                this.coolingIsActive = true;
            }

        },
        async setCompressorState() {

            let silverService = new SilverService()

            let response = await silverService.get_value_timestamp({
                device_name: 'f1255pc',
                observation_name: 'compressor_state',
                limit: 1
            })

            if (response.data[0]['value'] !== 20) {
                this.compressorIsActive = true
            } else {
                this.compressorIsActive = false
            }

        },
        async setHeatCircuitPumpState() {

            let silverService = new SilverService()

            let response = await silverService.get_value_timestamp({
                device_name: 'f1255pc',
                observation_name: 'heat_circuit_pump_speed',
                limit: 1
            })

            if (response.data[0]['value'] > 0) {
                this.heatCircuitPumpIsActive = true
            } else {
                this.heatCircuitPumpIsActive = false
            }

        },
        async setBrineCircuitPumpState() {

            let silverService = new SilverService()

            let response = await silverService.get_value_timestamp({
                device_name: 'f1255pc',
                observation_name: 'brine_circuit_pump_speed',
                limit: 1
            })

            if (response.data[0]['value'] > 0) {
                this.brineCircuitPumpIsActive = true
            } else {
                this.brineCircuitPumpIsActive = false
            }

        },
        async updateStatus() {

            this.setFunctionStatus()
            this.setCompressorState()
            this.setHeatCircuitPumpState()
            this.setBrineCircuitPumpState()

        }
    },
    mounted() {
        this.updateStatus()
        this.startPolling();
    },
    data() {
        return {
            compressorIsActive: false,
            heatCircuitPumpIsActive: false,
            brineCircuitPumpIsActive: false,
            coolingIsActive: false,
            heatingHouseIsActive: false,
            heatingWaterIsActive: false,
            observedAtTimestamp: "",
        }
    },
}
</script>
<style lang="scss" scoped>
.icon-small {
    width: 3.25rem;
    height: 3.25rem;
    margin-bottom: -0.5rem !important;
}

.icon-large {
    width: 6rem;
    height: 6rem;
}

.circle {
    border-radius: 50%;
    background-color: rgb(34, 37, 42);
}

.square {
    aspect-ratio: 1;
    margin-top: -2.5rem !important;
    max-height: 8rem !important;
    max-width: 8rem !important;
}
</style>