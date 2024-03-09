<template>
    <div class="container-fluid pt-2 px-4 h-100">
        <div class="row">
            <div class="col-md-12">
                <div class="row h-50">
                    <div class="col-md-3 p-3">
                        <silver-card-single-value title="Stove Left" deviceName="stove_left" observationName="current_power"
                            observationUnit="W" />
                    </div>
                    <div class="col-md-3 p-3">
                        <silver-card-single-value title="Stove Right" deviceName="stove_right"
                            observationName="current_power" observationUnit="W" />
                    </div>
                    <div class="col-md-3 p-3">
                        <silver-card-single-value title="WTW" deviceName="heat_recovery_ventilation"
                            observationName="current_power" observationUnit="W" />
                    </div>
                    <div class="col-md-3 p-3">
                        <silver-card-single-value title="Entertainment Station" deviceName="entertainment_station"
                            observationName="current_power" observationUnit="W" />
                    </div>
                </div>
            </div>
            <div class="col-md-12">
                <div class="row h-50">
                    <div class="col-md-3 p-3">
                        <silver-card-single-value title="Washing Machine" deviceName="washing_machine"
                            observationName="current_power" observationUnit="W" />
                    </div>
                    <div class="col-md-3 p-3">
                        <silver-card-single-value title="Bathroom Heater" deviceName="bathroom_heater"
                            observationName="current_power" observationUnit="W" />
                    </div>
                    <div class="col-md-3 p-3">
                        <silver-card-single-value title="Raspi Cluster" deviceName="raspi_cluster"
                            observationName="current_power" observationUnit="W" />
                    </div>
                    <div class="col-md-3 p-3">
                        <silver-card-single-value title="Quooker" deviceName="quooker" observationName="current_power"
                            observationUnit="W" />
                    </div>
                </div>
            </div>
            <div class="col-md-12">
                <div class="row h-50">
                    <div class="col-md-3 p-3">
                        <silver-card-single-value title="Oven" deviceName="oven" observationName="current_power"
                            observationUnit="W" />
                    </div>
                    <div class="col-md-3 p-3">
                        <silver-card-single-value title="Dishwasher" deviceName="dishwasher" observationName="current_power"
                            observationUnit="W" />
                    </div>
                    <div class="col-md-3 p-3">
                        <silver-card-single-value title="Fridge-freezer" deviceName="fridge_freezer"
                            observationName="current_power" observationUnit="W" />
                    </div>
                    <div class="col-md-3 p-3">
                        <silver-card-single-value title="Dryer" deviceName="dryer" observationName="current_power"
                            observationUnit="W" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="js">

import SilverCardSingleValue from '@/components/ui/standard-cards/SilverCardSingleValue.vue'

export default {
    name: 'AppliancesDashboardView',
    components: {
        SilverCardSingleValue,
    }
}
</script>
