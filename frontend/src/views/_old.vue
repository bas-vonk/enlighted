<template>
  <div class="container-fluid ">
    <div class="row">
      <div class="col-md-2 extra-padding card p-3 border-0">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title">Consumed from the grid:</h5>
            <p class="card-text fw-bold">{{ currentPower }}</p>
            <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
          </div>
        </div>
      </div>
      <div class="col-md-2 extra-padding card p-3 border-0">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title">Supplied from the grid:</h5>
            <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
            <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
          </div>
        </div>
      </div>
      <div class="col-md-2 extra-padding card p-3 border-0">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title">Fase 1 Current:</h5>
            <p class="card-text fw-bold">{{ currentL1 }}</p>
            <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
          </div>
        </div>
      </div>
      <div class="col-md-2 extra-padding card p-3 border-0">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title">Fase 2 Current:</h5>
            <p class="card-text fw-bold">{{ currentL2 }}</p>
            <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
          </div>
        </div>
      </div>
      <div class="col-md-2 extra-padding card p-3 border-0">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title">Fase 3 Current:</h5>
            <p class="card-text fw-bold">{{ currentL3 }}</p>
            <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
          </div>
        </div>
      </div>
      <div class="col-md-2 extra-padding card p-3 border-0">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title">Electricity price:</h5>
            <p class="card-text fw-bold">TODO</p>
            <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6 p-0">
        <div class="row p-1">
          <div class="col-md-4 card p-3 border-0">
            <div class="card text-center">
              <div class="card-body">
                <h5 class="card-title">Supplied from the grid:</h5>
                <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
              </div>
            </div>
          </div>
          <div class="col-md-4 card p-3 border-0">
            <div class="card text-center">
              <div class="card-body">
                <h5 class="card-title">Supplied from the grid:</h5>
                <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
              </div>
            </div>
          </div>
          <div class="col-md-4 card p-3 border-0">
            <div class="card text-center">
              <div class="card-body">
                <h5 class="card-title">Supplied from the grid:</h5>
                <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6 extra-padding card p-3 border-0">

      </div>
      <div class="col-md-2 extra-padding card p-3 border-0">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title">Supplied from the grid:</h5>
            <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
            <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6 extra-padding card">2</div>
      <div class="col-md-6 extra-padding card">3</div>
    </div>
    <div class="row">
      <div class="col-md-4 extra-padding card">2</div>
      <div class="col-md-4 extra-padding card">3</div>
      <div class="col-md-4 extra-padding card">4</div>
    </div>
    <div class="row">
      <div class="col-md-6">
        <div class="row py-2">
          <div class="col-md-4">
            <div class="card text-center">
              <div class="card-body">
                <h5 class="card-title">Supplied from the grid:</h5>
                <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card text-center">
              <div class="card-body">
                <h5 class="card-title">Supplied from the grid:</h5>
                <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card text-center">
              <div class="card-body">
                <h5 class="card-title">Supplied from the grid:</h5>
                <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
              </div>
            </div>
          </div>
        </div>
        <div class="row py-2">
          <div class="col-md-4">
            <div class="card text-center">
              <div class="card-body">
                <h5 class="card-title">Supplied from the grid:</h5>
                <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card text-center">
              <div class="card-body">
                <h5 class="card-title">Supplied from the grid:</h5>
                <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card text-center">
              <div class="card-body">
                <h5 class="card-title">Supplied from the grid:</h5>
                <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
              </div>
            </div>
          </div>
        </div>
        <div class="row py-2">
          <div class="col-md-4">
            <div class="card text-center">
              <div class="card-body">
                <h5 class="card-title">Supplied from the grid:</h5>
                <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card text-center">
              <div class="card-body">
                <h5 class="card-title">Supplied from the grid:</h5>
                <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card text-center">
              <div class="card-body">
                <h5 class="card-title">Supplied from the grid:</h5>
                <p class="card-text fw-bold">{{ currentPowerProduction }}</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
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
                <!-- <h5 class="card-title">Power usage</h5> -->
                <p class="card-text fw-bold">
                  <Line id="my-chart-id" :options="chartOptions" :data="chartData" ref="line" />
                </p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
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
    this.eventSource = new EventSource("http://localhost/live_power");
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
