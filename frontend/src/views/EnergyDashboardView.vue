<template>
    <div class="container-fluid pt-2 px-4 h-100">
        <div class="row">
            <div class="col-md-6">
                <div class="row py-2 h-50">
                    <div class="col-md-4">
                        <div class="card text-center bg-info h-100">
                            <div class="card-header bg-transparent">
                                <i class="bi bi-lightning-charge-fill"> Power purchased.</i>
                            </div>
                            <div class="card-body">
                                <p class="card-text">300W</p>
                                <small class="text-muted" style="font-size: 0.7rem;">Last updated 3 mins ago</small>

                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center bg-info h-100">
                            <div class="card-header bg-transparent">
                                <i class="bi bi-lightning-charge-fill"> Power purchased.</i>
                            </div>
                            <div class="card-body">
                                <p class="card-text">300W</p>
                                <small class="text-muted" style="font-size: 0.7rem;">Last updated 3 mins ago</small>

                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center bg-info h-100">
                            <div class="card-header bg-transparent">
                                <i class="bi bi-lightning-charge-fill"> Power purchased.</i>
                            </div>
                            <div class="card-body">
                                <p class="card-text">300W</p>
                                <small class="text-muted" style="font-size: 0.7rem;">Last updated 3 mins ago</small>

                            </div>
                        </div>
                    </div>
                </div>
                <div class="row py-2 h-50">
                    <div class="col-md-4">
                        <div class="card text-center bg-info h-100">
                            <div class="card-header bg-transparent">
                                <i class="bi bi-lightning-charge-fill"> Power purchased.</i>
                            </div>
                            <div class="card-body">
                                <p class="card-text">300W</p>
                                <small class="text-muted" style="font-size: 0.7rem;">Last updated 3 mins ago</small>

                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center bg-info h-100">
                            <div class="card-header bg-transparent">
                                <i class="bi bi-lightning-charge-fill"> Power purchased.</i>
                            </div>
                            <div class="card-body">
                                <p class="card-text">300W</p>
                                <small class="text-muted" style="font-size: 0.7rem;">Last updated 3 mins ago</small>

                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center bg-info h-100">
                            <div class="card-header bg-transparent">
                                <i class="bi bi-lightning-charge-fill"> Power purchased.</i>
                            </div>
                            <div class="card-body">
                                <p class="card-text">300W</p>
                                <small class="text-muted" style="font-size: 0.7rem;">Last updated 3 mins ago</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="row py-2 h-100">
                    <div class="col-md-12">
                        <div class="card text-center h-100">
                            <div class="card-body">
                                <h5 class="card-title">Power usage</h5>
                                <p class="card-text fw-bold">
                                    <Line id="chart" :options="chartOptions" :data="chartData" ref="line" />
                                </p>
                                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <div class="row py-2 h-100">
                    <div class="col-md-12">
                        <div class="card text-center bg-info h-100">
                            <div class="card-header bg-transparent">
                                <i class="bi bi-lightning-charge-fill">Table.</i>
                            </div>
                            <div class="card-body p-0">
                                <table class="table table-striped table-primary">
                                    <thead>
                                        <tr>
                                            <th scope="col">#</th>
                                            <th scope="col">First</th>
                                            <th scope="col">Last</th>
                                            <th scope="col">Handle</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <th scope="row">1</th>
                                            <td>Mark</td>
                                            <td>Otto</td>
                                            <td>@mdo</td>
                                        </tr>
                                        <tr>
                                            <th scope="row">2</th>
                                            <td>Jacob</td>
                                            <td>Thornton</td>
                                            <td>@fat</td>
                                        </tr>
                                        <tr>
                                            <th scope="row">2</th>
                                            <td>Jacob</td>
                                            <td>Thornton</td>
                                            <td>@fat</td>
                                        </tr>
                                        <tr>
                                            <th scope="row">2</th>
                                            <td>Jacob</td>
                                            <td>Thornton</td>
                                            <td>@fat</td>
                                        </tr>
                                        <tr>
                                            <th scope="row">2</th>
                                            <td>Jacob</td>
                                            <td>Thornton</td>
                                            <td>@fat</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="row py-2 h-50">
                    <div class="col-md-6">
                        <div class="card text-center bg-info h-100">
                            <div class="card-header bg-transparent">
                                <i class="bi bi-lightning-charge-fill"> Power purchased.</i>
                            </div>
                            <div class="card-body">
                                <p class="card-text">300W</p>
                                <small class="text-muted" style="font-size: 0.7rem;">Last updated 3 mins ago</small>

                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card text-center bg-info h-100">
                            <div class="card-header bg-transparent">
                                <i class="bi bi-lightning-charge-fill"> Power purchased.</i>
                            </div>
                            <div class="card-body">
                                <p class="card-text">300W</p>
                                <small class="text-muted" style="font-size: 0.7rem;">Last updated 3 mins ago</small>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row py-2 h-50">
                    <div class="col-md-6">
                        <div class="card text-center bg-info h-100">
                            <div class="card-header bg-transparent">
                                <i class="bi bi-lightning-charge-fill"> Power purchased.</i>
                            </div>
                            <div class="card-body">
                                <p class="card-text">300W</p>
                                <small class="text-muted" style="font-size: 0.7rem;">Last updated 3 mins ago</small>

                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card text-center bg-info h-100">
                            <div class="card-header bg-transparent">
                                <i class="bi bi-lightning-charge-fill"> Power purchased.</i>
                            </div>
                            <div class="card-body">
                                <p class="card-text">300W</p>
                                <small class="text-muted" style="font-size: 0.7rem;">Last updated 3 mins ago</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>

<script lang="ts">
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement)

export default {
    name: 'LineChart',
    components: { Line },
    mounted() {
        this.eventSource = new EventSource("http://localhost/bronze/live_power");
        this.eventSource.addEventListener('message', event => {
            var tibberMessage = JSON.parse(event.data)
            this.currentPower = tibberMessage.power
            this.currentPowerProduction = tibberMessage.powerProduction
            this.currentL1 = tibberMessage.currentL1
            this.currentL2 = tibberMessage.currentL2
            this.currentL3 = tibberMessage.currentL3
            this.chartDataLabels = [...this.chartDataLabels, tibberMessage.timestamp.slice(11, 19)].slice(-1800)
            this.chartDataPoints = [...this.chartDataPoints, tibberMessage.power].slice(-1800)
        }, false);
    },
    data() {
        return {
            eventSource: null,
            currentPower: null,
            currentPowerHistory: [],
            currentPowerProduction: null,
            currentL1: null,
            currentL2: null,
            currentL3: null,
            chartDataLabels: [],
            chartDataPoints: [],
        }
    },
    computed: {
        chartData() {
            return {
                labels: this.chartDataLabels,
                datasets: [
                    {
                        label: 'Power history',
                        data: this.chartDataPoints,
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }
                ]
            }
        },
        chartOptions() {
            return {
                animation: false,
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: false
                        },
                        ticks: {
                            autoSkip: true,
                            maxTicksLimit: 10
                        }
                    }
                }
            }
        }
    }
}
</script>

<style></style>
