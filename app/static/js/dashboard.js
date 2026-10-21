// Dashboard Charts rendering using Chart.js
document.addEventListener("DOMContentLoaded", function () {
  const lineCanvas = document.getElementById("scoreHistoryChart");
  const barCanvas = document.getElementById("notePerformanceChart");

  if (!lineCanvas && !barCanvas) return;

  fetch("/dashboard/data")
    .then(function (res) {
      if (!res.ok) throw new Error("Failed to load dashboard data");
      return res.json();
    })
    .then(function (data) {
      // Common chart defaults
      if (typeof Chart !== "undefined") {
        Chart.defaults.color = "#94a3b8";
        Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

        // 1. Line Chart: Score Percentage over time (last 20 attempts)
        if (lineCanvas) {
          const ctxLine = lineCanvas.getContext("2d");
          const labels = data.chart1.labels.length > 0 ? data.chart1.labels : ["No attempts yet"];
          const scores = data.chart1.scores.length > 0 ? data.chart1.scores : [0];

          new Chart(ctxLine, {
            type: "line",
            data: {
              labels: labels,
              datasets: [
                {
                  label: "Quiz Score (%)",
                  data: scores,
                  borderColor: "#d4af37",
                  backgroundColor: "rgba(212, 175, 55, 0.15)",
                  borderWidth: 2,
                  pointBackgroundColor: "#d4af37",
                  pointRadius: 4,
                  pointHoverRadius: 6,
                  fill: true,
                  tension: 0.3,
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  min: 0,
                  max: 100,
                  grid: { color: "rgba(255, 255, 255, 0.05)" },
                  ticks: {
                    callback: function (val) {
                      return val + "%";
                    },
                  },
                },
                x: {
                  grid: { color: "rgba(255, 255, 255, 0.05)" },
                },
              },
              plugins: {
                legend: { display: false },
                tooltip: {
                  callbacks: {
                    label: function (ctx) {
                      return "Score: " + ctx.raw + "%";
                    },
                  },
                },
              },
            },
          });
        }

        // 2. Bar Chart: Average Score per Note
        if (barCanvas) {
          const ctxBar = barCanvas.getContext("2d");
          const barLabels = data.chart2.labels.length > 0 ? data.chart2.labels : ["No note data yet"];
          const barScores = data.chart2.scores.length > 0 ? data.chart2.scores : [0];

          new Chart(ctxBar, {
            type: "bar",
            data: {
              labels: barLabels,
              datasets: [
                {
                  label: "Avg Score (%)",
                  data: barScores,
                  backgroundColor: "rgba(56, 189, 248, 0.6)",
                  borderColor: "#38bdf8",
                  borderWidth: 1,
                  borderRadius: 4,
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  min: 0,
                  max: 100,
                  grid: { color: "rgba(255, 255, 255, 0.05)" },
                  ticks: {
                    callback: function (val) {
                      return val + "%";
                    },
                  },
                },
                x: {
                  grid: { display: false },
                },
              },
              plugins: {
                legend: { display: false },
              },
            },
          });
        }
      }
    })
    .catch(function (err) {
      console.error("Dashboard chart error:", err);
    });
});
