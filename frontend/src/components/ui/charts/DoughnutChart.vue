<template>
    <Doughnut :data="chartData" :options="chartOptions" />
</template>

<script lang="js">
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

export default {
    name: 'DoughutChart',
    components: {
        Doughnut
    },
    props: {
        dataLabels: {
            default: [],
            type: Array
        },
        dataPointsPrimaryLabel: {
            default: '',
            type: String
        },
        dataPointsPrimary: {
            default: [],
            type: Array
        },
        dataPointsSecondaryLabel: {
            default: '',
            type: String
        },
        dataPointsSecondary: {
            default: [],
            type: Array
        }
    },
    computed: {
        chartData() {
            return {
                labels: this.dataLabels,
                datasets: [
                    {
                        label: this.dataPointsPrimaryLabel,
                        backgroundColor: this.dataLabels.map(label => this.colorPerLabel[label]),
                        data: this.dataPointsPrimary,
                        borderWidth: 5,
                        borderColor: "rgb(52, 58, 63)"
                    },
                    {
                        label: this.dataPointsSecondaryLabel,
                        backgroundColor: this.dataLabels.map(label => this.colorPerLabel[label]),
                        data: this.dataPointsSecondary,
                        borderWidth: 5,
                        borderColor: "rgb(52, 58, 63)"
                    }

                ]
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
    },
    data() {
        return {
            colorPerLabel: {
                Cheap: '#10CAF0',
                Average: '#6F42C1',
                Expensive: '#D63384'
            }
        }
    }
}
</script>