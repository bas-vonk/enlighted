<template>
    <Line :options="chartOptions" :data="chartData" ref="line" />
</template>

<script>
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Tooltip, LineElement, Filler } from 'chart.js'

ChartJS.register(Tooltip, LineElement, Filler)

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
        datasets: {
            default: [],
            type: Array
        },
        observedAtTimestamp: {
            default: "",
            type: String
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
                            maxTicksLimit: 20,
                            callback: function (val, index) {
                                const unixTimestamp = this.getLabelForValue(val)
                                return new Date(unixTimestamp * 1000).toLocaleString(undefined, {
                                    month: "numeric", day: "numeric",
                                    hour: "numeric", minute: "numeric"
                                })
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
                    // decimation: {
                    //     enabled: true,
                    //     algorithm: 'lttb',
                    //     samples: 50
                    // }
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
