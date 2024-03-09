<template>
    <Line :options="chartOptions" :data="chartData" />
</template>

<script>
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Tooltip, LineElement, Filler } from 'chart.js'
import { TimeHelpers } from '@/helpers/helpers.js'

ChartJS.register(Tooltip, LineElement, Filler)

export default {
    name: 'StackedLineChart',
    components: {
        Line,
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
