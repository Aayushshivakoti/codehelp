<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "vue-chartjs";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default {
  name: "LineChart",
  components: {
    Line,
  },
  props: {
    data: {
      type: Array,
      required: true,
    },
    labels: {
      type: Array,
      required: true,
    },
    title: {
      type: String,
      default: "Performance Over Time",
    },
    ySuffix: {
      type: String,
      default: "%",
    },
    beginAtZero: {
      type: Boolean,
      default: true,
    },
    max: {
      type: Number,
      default: 100,
    },
    datasetLabel: {
      type: String,
      default: "Score",
    },
  },
  computed: {
    chartData() {
      return {
        labels: this.labels,
        datasets: [
          {
            label: this.datasetLabel,
            data: this.data,
            borderColor: "#3b82f6",
            backgroundColor: "rgba(59, 130, 246, 0.1)",
            tension: 0.4,
            fill: true,
          },
        ],
      };
    },
    chartOptions() {
      const self = this;
      const yScale = {
        beginAtZero: this.beginAtZero,
      };
      if (this.max !== null && this.max !== undefined) {
        yScale.max = this.max;
      }
      yScale.ticks = {
        callback: function (value) {
          return value + self.ySuffix;
        },
      };

      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: this.title,
            font: {
              size: 16,
              weight: "bold",
            },
          },
          legend: {
            display: false,
          },
        },
        scales: {
          y: yScale,
        },
      };
    },
  },
};
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}
</style>
