<template>
    <Line :options="chartOptions" :data="chartData" />
</template>

<script>
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Tooltip, LineElement, Filler } from 'chart.js'
import { TimeHelpers } from '@/helpers/helpers.js'

ChartJS.register(Tooltip, LineElement, Filler)

export default {
    name: 'LineChart',
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
                animation: false,
                parsing: false,
                responsive: true,
                elements: {
                    point: {
                        radius: 0
                    },
                },
                scales: {
                    x: {
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
                            display: true
                        },
                        border: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        drawOnChartArea: false,
                        ticks: {
                            display: true,
                            fontColor: 'black',
                            color: 'white',
                            font: {
                                family: 'Aharoni Bold V1',
                                size: 25
                            }
                        },
                        grid: {
                            display: true,
                            lineWidth: ({ tick }) => tick.value == 0 ? 1 : 0.5
                        },
                        border: {
                            display: false
                        }
                    }
                },

                plugins: {
                    legend: {
                        display: true,
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            title: function (context) {
                                const unixTimestamp = context[0].label
                                return new Date(unixTimestamp * 1000).toLocaleString(undefined, {
                                    month: "numeric", day: "numeric",
                                    hour: "numeric", minute: "numeric"
                                })
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
