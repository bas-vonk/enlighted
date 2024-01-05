<template>
    <Doughnut :data="chartData" :options="chartOptions" />
</template>

<script>
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

export default {
    name: 'DoughutChart',
    components: {
        Doughnut
    },
    props: {
        labels: {
            default: false,
            type: Array
        },
        datasets: {
            default: false,
            type: Array
        }
    },
    computed: {
        chartData() {
            return {
                labels: this.labels,
                datasets: this.datasets
            }
        },
        chartOptions() {
            return {
                elements: {
                    arc: {
                        borderWidth: 0
                    }
                },
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        }
    }
}
</script>