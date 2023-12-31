<template>
    <div class="container-fluid pt-2 px-4 h-100">
        <div class="row">
            <div class="col-md-6">
                <div class="row h-50">
                    <div class="col-md-8 p-3">
                        <heat-pump-status-card />
                    </div>
                    <div class="col-md-4 p-3">
                        <spa-refrigerant-correction-card />
                    </div>
                </div>
                <div class="row h-50">
                    <div class="col-md-6 p-3">
                        <indoor-temperature-card />
                    </div>
                    <div class="col-md-6 p-3">
                        <outdoor-temperature-card />
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="row py-3">
                    <div class="col-md-12">
                        <operating-hours-card />
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <div class="row h-100">
                    <div class="col-md-12 p-3">
                        <historical-temperatures-card />
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="row h-50">
                    <div class="col-md-6 p-3">
                        <refrigerant-temperature-card />
                    </div>
                    <div class="col-md-6 p-3">
                        <refrigerant-temperature-diff-card />
                    </div>
                </div>
                <div class="row h-50">
                    <div class="col-md-6 p-3">
                        <brine-temperature-card />
                    </div>
                    <div class="col-md-6 p-3">
                        <degree-minutes-card />
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-12">
                <div class="row">
                    <div class=" col-md-12 p-3">
                        <historical-system-status-card />
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>

<script lang="js">

import HeatPumpStatusCard from '@/components/cards/heating/HeatPumpStatusCard.vue'
import IndoorTemperatureCard from '@/components/cards/heating/IndoorTemperatureCard.vue'
import OutdoorTemperatureCard from '@/components/cards/heating/OutdoorTemperatureCard.vue'
import DegreeMinutesCard from '@/components/cards/heating/DegreeMinutesCard.vue'
import OperatingHoursCard from '@/components/cards/heating/OperatingHoursCard.vue'
import RefrigerantTemperatureCard from '@/components/cards/heating/RefrigerantTemperatureCard.vue'
import RefrigerantTemperatureDiffCard from '@/components/cards/heating/RefrigerantTemperatureDiffCard.vue'
import BrineTemperatureCard from '@/components/cards/heating/BrineTemperatureCard.vue'
import SpaRefrigerantCorrectionCard from '@/components/cards/heating/SpaRefrigerantCorrectionCard.vue'
import HistoricalTemperaturesCard from '@/components/cards/heating/HistoricalTemperaturesCard.vue'
import HistoricalSystemStatusCard from '@/components/cards/heating/HistoricalSystemStatusCard.vue'

export default {
    name: 'HeatingDashboardView',
    components: {
        HeatPumpStatusCard,
        IndoorTemperatureCard,
        OutdoorTemperatureCard,
        DegreeMinutesCard,
        OperatingHoursCard,
        RefrigerantTemperatureCard,
        RefrigerantTemperatureDiffCard,
        BrineTemperatureCard,
        SpaRefrigerantCorrectionCard,
        HistoricalTemperaturesCard,
        HistoricalSystemStatusCard
    },
}
</script>
