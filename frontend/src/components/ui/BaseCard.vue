<template>
    <div class="card rounded-5 text-center h-100">
        <div class="card-header bg-transparent">
            <div>
                <slot name="header"></slot>
            </div>
            <small class="observed_at">Observed at: {{ observedAtTimestamp }}</small>
        </div>
        <div class="card-body rounded-5">
            <slot v-if="isMeasuredReliably" name="body"></slot>
            <div v-else class="justify-content-center d-flex align-items-center p-4">Data not reliable.
            </div>
        </div>
    </div>
</template>

<script>

export default {
    name: "BaseCard",
    props: {
        observedAtTimestamp: {
            default: "",
            type: String
        },
        isMeasuredReliably: {
            default: true,
            type: Boolean
        }
    },
    data() {
        return {

        }
    }
}
</script>

<style lang="scss" scoped>
@import "@/../node_modules/bootstrap/scss/bootstrap";

.card {
    font-family: "Aharoni Bold V1" !important;
    background-color: $gray-800 !important;
    border-width: 0rem !important;
    text-align: left !important;
}

.card-header {
    border-width: 0rem !important;
    font-size: 1.5rem;
    color: white;
    padding: 0.75rem 0.5rem 0.5rem 1.5rem;
    line-height: 1.75rem;
    white-space: nowrap;
}

.card-body {
    padding: 0.5rem 0.5rem 0.5rem 0.5rem !important;
    border-width: 0rem !important;
    text-align: right !important;
    font-family: "Aharoni Bold V1";
    color: white;
}

.observed_at {
    font-size: 0.8rem !important;
    color: white !important;
    font-weight: lighter !important;
    font-family: Calibri, sans-serif
}
</style>