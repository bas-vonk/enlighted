<template>
    <div class="container-fluid pt-2 px-4 h-100">
        <div class="row">
            <div class="col-md-6">
                <div class="row h-50">
                    <div class="col-md-8 p-3">
                        <heat-pump-current-status-card />
                    </div>
                    <div class="col-md-4 p-3">
                        <silver-card-single-value title="SPA corr." deviceName="f1255pc"
                            observationName="smart_price_adaption_temperature_correction" />
                    </div>
                </div>
                <div class="row h-50">
                    <div class="col-md-6 p-3">
                        <silver-card-single-value-with-sparkline title="Indoor temperature" deviceName="f1255pc"
                            observationName="room_temperature" observationUnit="&#176;C" />
                    </div>
                    <div class="col-md-6 p-3">
                        <silver-card-single-value-with-sparkline title="Outdoor temperature" deviceName="f1255pc"
                            observationName="outdoor_temperature" observationUnit="&#176;C" />
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="row py-3">
                    <div class="col-md-12">
                        <heat-pump-operating-hours-card />
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <div class="row h-100">
                    <div class="col-md-12 p-3">
                        <temperature-history-card />
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="row h-50">
                    <div class="col-md-6 p-3">
                        <silver-card-double-value title="Heat circuit" deviceNameLeft="f1255pc"
                            observationNameLeft="heat_medium_flow_temperature" observationUnitLeft="&#176;C"
                            observationExplanationLeft="To house" deviceNameRight="f1255pc"
                            observationNameRight="heat_medium_flow_return_temperature" observationUnitRight="&#176;C"
                            observationExplanationRight="From house" isNotReliableDeviceName="f1255pc"
                            isNotReliableObservationName="heat_circuit_pump_speed" :isNotReliableObservationValue="0" />
                    </div>
                    <div class="col-md-6 p-3">
                        <silver-card-double-value title="Supply temp" deviceNameLeft="f1255pc"
                            observationNameLeft="heat_medium_flow_temperature" observationUnitLeft="&#176;C"
                            observationExplanationLeft="Actual" deviceNameRight="f1255pc"
                            observationNameRight="heat_medium_flow_calculated_temperature" observationUnitRight="&#176;C"
                            observationExplanationRight="Calculated" isNotReliableDeviceName="f1255pc"
                            isNotReliableObservationName="heat_circuit_pump_speed" :isNotReliableObservationValue="0" />
                    </div>
                </div>
                <div class="row h-50">
                    <div class="col-md-6 p-3">
                        <silver-card-double-value title="Brine circuit" deviceNameLeft="f1255pc"
                            observationNameLeft="temperature_brine_out" observationUnitLeft="&#176;C"
                            observationExplanationLeft="Brine out" deviceNameRight="f1255pc"
                            observationNameRight="temperature_brine_in" observationUnitRight="&#176;C"
                            observationExplanationRight="Brine in" isNotReliableDeviceName="f1255pc"
                            isNotReliableObservationName="brine_circuit_pump_speed" :isNotReliableObservationValue="0" />
                    </div>
                    <div class="col-md-6 p-3">
                        <silver-card-single-value-with-sparkline title="Degree minutes" deviceName="f1255pc"
                            observationName="degree_minutes" parameterUnit="" />
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-12">
                <div class="row">
                    <div class=" col-md-12 p-3">
                        <heat-pump-historical-status-card />
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>

<script lang="js">

import SilverCardDoubleValue from '@/components/ui/standard-cards/SilverCardDoubleValue.vue'
import SilverCardSingleValue from '@/components/ui/standard-cards/SilverCardSingleValue.vue'
import SilverCardSingleValueWithSparkline from '@/components/ui/standard-cards/SilverCardSingleValueWithSparkline.vue'

import HeatPumpCurrentStatusCard from '@/components/cards/heating/HeatPumpCurrentStatusCard.vue'
import HeatPumpOperatingHoursCard from '@/components/cards/heating/HeatPumpOperatingHoursCard.vue'
import TemperatureHistoryCard from '@/components/cards/heating/TemperatureHistoryCard.vue'
import HeatPumpHistoricalStatusCard from '@/components/cards/heating/HeatPumpHistoricalStatusCard.vue'

export default {
    name: 'HeatingDashboardView',
    components: {
        SilverCardDoubleValue,
        SilverCardSingleValue,
        SilverCardSingleValueWithSparkline,
        HeatPumpCurrentStatusCard,
        HeatPumpOperatingHoursCard,
        HeatPumpHistoricalStatusCard,
        TemperatureHistoryCard,
    }
}
</script>
