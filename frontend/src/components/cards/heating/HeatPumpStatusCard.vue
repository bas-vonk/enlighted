<template>
    <base-card :observedAtTimestamp="observedAtTimestamp">
        <template v-slot:header>Heat pump status</template>
        <template v-slot:body>
            <div class="rounded-5">
                <div class="row px-4">
                    <div class="col p-0 d-flex justify-content-left align-items-end">
                        <compressor-icon
                            :class="{ 'icon-orange': compressorIsActive, 'icon-inactive': !compressorIsActive }"
                            class="icon-small p-1">
                        </compressor-icon>
                    </div>
                    <div class="col p-0 d-flex justify-content-left align-items-end">
                        <refrigerant-pump-icon
                            :class="{ 'icon-orange': refrigerantPumpIsActive, 'icon-inactive': !refrigerantPumpIsActive }"
                            class="icon-small p-1">
                        </refrigerant-pump-icon>
                    </div>
                    <div class="col p-0 d-flex justify-content-left align-items-end">
                        <brine-pump-icon
                            :class="{ 'icon-orange': brinePumpIsActive, 'icon-inactive': !brinePumpIsActive, 'icon-small': true }"
                            class="icon-small p-1">
                        </brine-pump-icon>
                    </div>
                    <div class="col-4 p-0 circle square d-flex justify-content-center align-items-center">
                        <cooling-icon v-if="coolingIsActive" class="icon-large icon-blue" />
                        <heating-house-icon v-else-if="heatingHouseIsActive" class=" icon-large icon-pink" />
                        <heating-water-icon v-else-if="heatingWaterIsActive" class="icon-large icon-pink" />
                        <sleep-icon v-else class="icon-large" />
                    </div>
                </div>
            </div>
        </template>
    </base-card>
</template>

<script>
import axios from 'axios'

import BaseCard from '@/components/ui/BaseCard.vue'
import BrinePumpIcon from '@/components/icons/BrinePumpIcon.vue'
import RefrigerantPumpIcon from '@/components/icons/RefrigerantPumpIcon.vue'
import CompressorIcon from '@/components/icons/CompressorIcon.vue'
import SleepIcon from '@/components/icons/SleepIcon.vue'
import CoolingIcon from '@/components/icons/CoolingIcon.vue'
import HeatingHouseIcon from '@/components/icons/HeatingHouseIcon.vue'
import HeatingWaterIcon from '@/components/icons/HeatingWaterIcon.vue'


export default {
    name: 'SingleImageCard',
    components: { BaseCard, BrinePumpIcon, RefrigerantPumpIcon, CompressorIcon, SleepIcon, CoolingIcon, HeatingHouseIcon, HeatingWaterIcon },
    methods: {
        resetFunctionStatus() {
            this.coolingIsActive = false;
            this.heatingHouseIsActive = false;
            this.heatingWaterIsActive = false;
        },
        resetComponentStatus() {
            this.compressorIsActive = false;
            this.refrigerantPumpIsActive = false;
            this.brinePumpIsActive = false;
        },
        startPolling() {
            this.intervalId = setInterval(this.fetchData, 10000)
        },
        async fetchData() {

            // Update information on functions
            const response_system_status = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=system_status&limit=1")

            // Update observed at timestamp
            this.observedAtTimestamp = new Date(response_system_status.data.data[0].observed_at * 1000).toLocaleString(undefined, {
                month: "numeric", day: "numeric",
                hour: "numeric", minute: "numeric"
            })

            this.resetFunctionStatus()
            if (response_system_status.data.data[0]['value'] === 1) {
                this.heatingWaterIsActive = true;
            } else if (response_system_status.data.data[0]['value'] === 2) {
                this.heatingHouseIsActive = true;
            } else if (response_system_status.data.data[0]['value'] === 4) {
                this.coolingIsActive = true;
            }

            // Update information on components
            const response_compressor_state = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=compressor_state&limit=1")
            const response_heat_circuit_pump_speed = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=heat_circuit_pump_speed&limit=1")
            const response_brine_circuit_pump_speed = await axios.get("http://localhost/silver/value_timestamp?device_name=f1255pc&observation_name=brine_circuit_pump_speed&limit=1")

            this.resetComponentStatus()
            if (response_compressor_state.data.data[0]['value'] !== 20) {
                this.compressorIsActive = true
            }
            if (response_heat_circuit_pump_speed.data.data[0].value > 0) {
                this.refrigerantPumpIsActive = true;
            }
            if (response_brine_circuit_pump_speed.data.data[0].value > 0) {
                this.brinePumpIsActive = true;
            }


            // this.currentValue = this.data[0]['value']
            // this.currentValueTimestamp = new Date(this.data[0]['observed_at'] * 1000);
            // this.currentValueTimestamp = this.currentValueTimestamp.toLocaleString(undefined, {
            //     month: "numeric", day: "numeric",
            //     hour: "numeric", minute: "numeric"
            // });
            // this.dataLabels = response.data.data.map(item => new Date(item.observed_at * 1000).toLocaleString(undefined, {
            //     month: "numeric", day: "numeric",
            //     hour: "numeric", minute: "numeric"
            // })).reverse();
        }
    },
    mounted() {
        this.fetchData()
        this.startPolling();
    },
    data() {
        return {
            compressorIsActive: false,
            refrigerantPumpIsActive: false,
            brinePumpIsActive: false,
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
}
</style>