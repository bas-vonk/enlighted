<template>
    <base-card :observedAtTimestamp="observedAtTimestamp" :isMeasuredReliably="isMeasuredReliably">
        <template v-slot:header>{{ title }}</template>
        <template v-slot:body>
            <div class="row h-100">
                <div class="col-5 left">
                    <span style="position: absolute; margin-left: 0.25rem; margin-top: 3rem; font-size: 0.75rem;">
                        {{ observationExplanationLeft }}
                    </span>
                    <div class="display-1" style="line-height: 2.5rem;">
                        <span>{{ Math.round(leftValue, 1) }}</span>
                        <span v-html="observationUnitLeft" class="unit"></span>
                    </div>
                </div>
                <div class="col-2 middle">
                    <div class="vr"></div>
                </div>
                <div class="col-5 right">
                    <div class="display-1" style="line-height: 2.5rem;">
                        <span>{{ Math.round(rightValue, 1) }}</span>
                        <span v-html="observationUnitRight" class="unit"></span>
                    </div>
                    <span style="position: absolute; margin-right: 0rem; margin-bottom: 3.5rem; font-size: 0.75rem;">
                        {{ observationExplanationRight }}
                    </span>
                </div>
            </div>
        </template>
    </base-card>
</template>

<script>

import BaseCard from '@/components/ui/BaseCard.vue'
import { SilverService } from '@/services/silver.js'
import { TimeHelpers } from '@/helpers/helpers.js'

export default {
    name: 'SingleImageCard',
    components: { BaseCard },
    props: {
        title: {
            default: "",
            type: String
        },
        deviceNameLeft: {
            default: false,
            type: String
        },
        observationNameLeft: {
            default: false,
            type: String
        },
        observationUnitLeft: {
            default: "",
            type: String
        },
        observationExplanationLeft: {
            default: false,
            type: String
        },
        deviceNameRight: {
            default: false,
            type: String
        },
        observationNameRight: {
            default: false,
            type: String
        },
        observationUnitRight: {
            default: "",
            type: String
        },
        observationExplanationRight: {
            default: false,
            type: String
        },
        isNotReliableDeviceName: {
            default: null,
            type: String
        },
        isNotReliableObservationName: {
            default: null,
            type: String
        },
        isNotReliableObservationValue: {
            default: null,
            type: Number
        }
    },
    methods: {
        startPolling() {
            this.intervalId = setInterval(this.fetchData, 60000)
        },
        async fetchData() {

            let silverService = new SilverService()

            // First check reliability of the data
            if (this.isNotReliableDeviceName !== null) {

                // Get the data that is used to determine the reliability
                let response_reliability = await silverService.get_value_timestamp({
                    device_name: this.isNotReliableDeviceName,
                    observation_name: this.isNotReliableObservationName,
                    limit: 1
                })

                // Run the check
                if (response_reliability.data[0].value === this.isNotReliableObservationValue) {
                    this.isMeasuredReliably = false
                    return
                } else {
                    this.isMeasuredReliably = true
                }

            }

            // Fetch the data for left
            let response_left = await silverService.get_value_timestamp({
                device_name: this.deviceNameLeft,
                observation_name: this.observationNameLeft,
                limit: 1
            })
            this.leftValue = response_left.data[0].value;
            this.leftObservedAtTimestamp = TimeHelpers.getHRFShort(response_left.data[0].observed_at)

            // Fetch the data for right
            let response_right = await silverService.get_value_timestamp({
                device_name: this.deviceNameRight,
                observation_name: this.observationNameRight,
                limit: 1
            })
            this.rightValue = response_right.data[0].value;
            this.rightObservedAtTimestamp = TimeHelpers.getHRFShort(response_right.data[0].observed_at)

            // Define the observed timestamp
            this.observedAtTimestamp = this.leftObservedAtTimestamp;
        }
    },
    mounted() {
        this.fetchData()
        this.startPolling();
    },
    data() {
        return {
            observedAtTimestamp: "",
            leftValue: null,
            rightValue: null,
            isMeasuredReliably: true
        }
    }
}
</script>
<style lang="scss" scoped>
.vr {
    transform: rotate(45deg);
    height: 100%;
}

.top {
    align-self: flex-start;
}

.bottom {
    margin-top: auto;
}

.left {
    align-items: flex-start !important;
    text-align: left !important;
    display: flex !important;
    overflow: visible !important;
    white-space: nowrap !important;
    direction: ltr !important;
    padding-left: 2rem !important;
    padding-top: 0.5rem !important;
}

.middle {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;

}

.right {
    align-items: flex-end !important;
    text-align: right !important;
    display: flex !important;
    overflow: visible !important;
    white-space: nowrap !important;
    direction: rtl !important;
    padding-right: 2rem !important;
}
</style>