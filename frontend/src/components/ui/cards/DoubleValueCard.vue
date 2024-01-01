<template>
    <base-card :observedAtTimestamp="observedAtTimestamp" :isMeasuredReliably="isMeasuredReliably">
        <template v-slot:header>{{ this.cardTitle }}</template>
        <template v-slot:body>
            <div class="row h-100">
                <div class="col-5 left">
                    <span style="position: absolute; margin-left: 0.25rem; margin-top: 3rem; font-size: 0.75rem;">{{
                        this.leftExplanation
                    }}</span>
                    <div class="display-1" style="line-height: 2.5rem;"><span>{{ Math.round(this.leftValue) }}</span><span
                            v-html="rightUnit" class="unit"></span>
                    </div>
                </div>
                <div class="col-2 middle">
                    <div class="vr"></div>
                </div>
                <div class="col-5 right">
                    <div class="display-1" style="line-height: 2.5rem;"><span>{{ Math.round(this.rightValue) }}</span><span
                            v-html="rightUnit" class="unit"></span>
                    </div><span
                        style="position: absolute; margin-right: 0rem; margin-bottom: 3.5rem; font-size: 0.75rem;">{{
                            this.rightExplanation
                        }}</span>
                </div>
            </div>
        </template>
    </base-card>
</template>

<script>
import axios from 'axios'

import BaseCard from '@/components/ui/BaseCard.vue'

export default {
    name: 'SingleImageCard',
    components: { BaseCard },
    props: {
        cardTitle: {
            default: "",
            type: String
        },
        observedAtTimestamp: {
            default: "",
            type: String
        },
        leftValue: {
            default: null,
            type: Number,
        },
        leftUnit: {
            default: "",
            type: String
        },
        leftExplanation: {
            default: "",
            type: String
        },
        rightValue: {
            default: null,
            type: Number,
        },
        rightUnit: {
            default: "",
            type: String
        },
        rightExplanation: {
            default: "",
            type: String
        },
        isMeasuredReliably: {
            default: true,
            type: Boolean
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