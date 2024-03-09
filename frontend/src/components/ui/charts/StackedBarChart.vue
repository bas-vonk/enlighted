<template>
    <Bar :options="chartOptions" :data="chartData" />
</template>

<script>
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Tooltip, BarElement, Filler } from 'chart.js'
import { TimeHelpers } from '@/helpers/helpers.js'

ChartJS.register(Tooltip, BarElement, Filler)

export default {
    name: 'StackedBarChart',
    components: {
        Bar,
    },
    props: {
        labels: {
            default: [],
            type: Array
        },
        datasets: {
            default: [],
            type: Array
        }
    },
    computed: {
        chartOptions() {
            return {
                responsive: true,
                barPercentage: 1.0, // Set the width of the bars to 100% of available space
                categoryPercentage: 1.0, // Set the spacing between bars to 0
                scales: {
                    x: {
                        stacked: true,
                        ticks: {
                            display: true,
                            autoSkip: true,
                            maxTicksLimit: 10,
                            callback: function (val, index) {
                                let unixTimestamp = this.getLabelForValue(val)
                                return TimeHelpers.getHRFShort(unixTimestamp)
                            }
                        },
                        grid: {
                            display: false
                        },
                        border: {
                            display: false
                        }
                    },
                    y1: {
                        stack: 'stacked',
                        stackWeight: 0.25,
                        beginAtZero: true,
                        ticks: {
                            display: true,
                            fontColor: 'black',
                            color: 'white',
                            callback: function (value, index, values) {
                                return value + 'ct';
                            }
                        },
                        grid: {
                            display: true,
                            lineWidth: ({ tick }) => tick.value == 0 ? 1 : 0
                        },
                        border: {
                            display: false
                        }
                    },
                    y2: {
                        stack: 'stacked',
                        stacked: true,
                        stackWeight: 0.75,
                        offset: true,
                        beginAtZero: true,
                        ticks: {
                            display: true,
                            fontColor: 'black',
                            color: 'white',
                            callback: function (value, index, values) {
                                return value + 'Wh';
                            }
                        },
                        grid: {
                            display: true,
                            lineWidth: ({ tick }) => tick.value == 0 ? 1 : 0
                        },
                        border: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    },
                    tooltip: {
                        mode: 'index',
                        callbacks: {
                            title: function (context) {
                                const unixTimestampWindowStart = context[0].label
                                const unixTimestampWindowEnd = String(parseInt(unixTimestampWindowStart) + 3600)
                                return TimeHelpers.getHRFShort(unixTimestampWindowStart) + ' - ' + TimeHelpers.getHRFHoursMinutes(unixTimestampWindowEnd)

                            }
                        }
                    },
                }
            }
        },
        chartData() {
            return {
                labels: this.labels,
                datasets: this.datasets
            }
        }

    }
}
</script>
