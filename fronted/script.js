// TODO: person 1 has to add the uzure function url after deploying the backend
//replace this one with the real azure url, this is just a place holder: const FUNCTION_URL = "https://<your-function-app>.azurewebsites.net/api/<your-function-name>";
const barCanvas = document.getElementById("barChart");
const scatterCanvas = document.getElementById("scatterPlot");
const pieCanvas = document.getElementById("pieChart");
const heatmapDiv = document.getElementById("heatmap");
const metadataEl = document.getElementById("metadata");

const dietSearch = document.getElementById("dietSearch");
const dietSelect = document.getElementById("dietSelect");
const btnInsights = document.getElementById("btnInsights");

// fetch data from backend
async function fetchInsights() {
  try {
    const url = new URL(FUNCTION_URL);
    url.searchParams.set("dietType", dietSelect.value);
    url.searchParams.set("search", dietSearch.value);

    const res = await fetch(url);
    const data = await res.json();

    // TODO: Person 1 has to return data in this kind of fromat
    // { barData: { labels: [], values: [] }, scatterData: { points: [] }, pieData: { labels: [], values: [] }, heatmapData: [], executionTime: "123ms" }

    renderBarChart(data.barData);
    renderScatterChart(data.scatterData);
    renderPieChart(data.pieData);
    renderHeatmap(data.heatmapData);
    renderMetadata(data.executionTime);
  } catch (err) {
    console.error("Error fetching insights:", err);
  }
}

let barChartInstance;
function renderBarChart(barData) {
  if (barChartInstance) barChartInstance.destroy();
  barChartInstance = new Chart(barCanvas, {
    type: "bar",
    data: {
      labels: barData.labels,
      datasets: [{
        label: "Average Macronutrients",
        data: barData.values,
        backgroundColor: "rgba(37, 99, 235, 0.6)"
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

let scatterChartInstance;
function renderScatterChart(scatterData) {
  if (scatterChartInstance) scatterChartInstance.destroy();
  scatterChartInstance = new Chart(scatterCanvas, {
    type: "scatter",
    data: {
      datasets: [{
        label: "Protein vs Carbs",
        data: scatterData.points,
        backgroundColor: "rgba(16, 185, 129, 0.6)"
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

let pieChartInstance;
function renderPieChart(pieData) {
  if (pieChartInstance) pieChartInstance.destroy();
  pieChartInstance = new Chart(pieCanvas, {
    type: "pie",
    data: {
      labels: pieData.labels,
      datasets: [{
        data: pieData.values,
        backgroundColor: [
          "rgba(59, 130, 246, 0.7)",
          "rgba(234, 179, 8, 0.7)",
          "rgba(239, 68, 68, 0.7)"
        ]
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

function renderHeatmap(heatmapData) {
  heatmapDiv.textContent = "Heatmap visualization goes here.";
}

function renderMetadata(executionTime) {
  metadataEl.textContent = `Execution time: ${executionTime}`;
}

// button click
btnInsights.addEventListener("click", () => {
  fetchInsights();
});

// initial load
document.addEventListener("DOMContentLoaded", () => {
  fetchInsights();
});