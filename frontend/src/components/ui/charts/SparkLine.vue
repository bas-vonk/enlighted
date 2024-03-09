<template>
    <Line :options="chartOptions" :data="chartData" />
</template>

<script>
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Tooltip, LineElement, Filler, LinearScale, CategoryScale, PointElement } from 'chart.js'

ChartJS.register(Tooltip, LineElement, Filler, LinearScale, CategoryScale, PointElement)

export default {
    name: 'SparkLine',
    components: {
        Line,
    },
    props: {
        labels: {
            default: [],
            type: Array
        },
        dataPoints: {
            default: [],
            type: Array
        }
    },
    computed: {
        chartOptions() {
            return {
                animation: false,
                responsive: true,
                elements: {
                    point: {
                        radius: 0
                    },
                },
                scales: {
                    x: {
                        ticks: {
                            display: false
                        },
                        grid: {
                            display: false
                        },
                        border: {
                            display: false
                        }
                    },
                    y: {
                        ticks: {
                            display: false,
                        },
                        grid: {
                            display: false,
                        },
                        border: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        },
        chartData() {
            return {
                labels: this.labels,
                datasets: [{
                    data: this.dataPoints,
                    borderColor: 'white',
                    borderWidth: 1.5,
                    tension: 0.3
                }]
            }
        }

    }
}
</script>
