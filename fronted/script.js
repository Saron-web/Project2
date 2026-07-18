const FUNCTION_URL = "https://rishabh-diet-function-2026-crh8cfbxfhhybmf4.mexicocentral-01.azurewebsites.net/api/get_nutritional_insights";
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
    metadataEl.textContent = "Loading insights...";
    const url = new URL(FUNCTION_URL);

    // Set query params if they are not default
    const selectedDiet = dietSelect.value;
    if (selectedDiet && selectedDiet !== "all") {
      url.searchParams.set("dietType", selectedDiet);
    }

    const searchVal = dietSearch.value.trim();
    if (searchVal) {
      url.searchParams.set("search", searchVal);
    }

    console.log("Fetching from URL:", url.toString());
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    const data = await res.json();
    console.log("Data received:", data);

    // Format check / default values in case of missing keys
    const barData = data.barData || { labels: [], values: [] };
    const scatterData = data.scatterData || { points: [] };
    const pieData = data.pieData || { labels: [], values: [] };
    const heatmapData = data.heatmapData || [];
    const executionTime = data.executionTime || "N/A";

    renderBarChart(barData);
    renderScatterChart(scatterData);
    renderPieChart(pieData);
    renderHeatmap(heatmapData);
    renderMetadata(executionTime);
  } catch (err) {
    console.error("Error fetching insights:", err);
    metadataEl.textContent = `Error fetching insights: ${err.message}`;
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
        backgroundColor: [
          "rgba(37, 99, 235, 0.7)", // Protein
          "rgba(245, 158, 11, 0.7)", // Carbs
          "rgba(16, 185, 129, 0.7)"  // Fat
        ],
        borderColor: [
          "rgb(37, 99, 235)",
          "rgb(245, 158, 11)",
          "rgb(16, 185, 129)"
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Amount (g)'
          }
        }
      }
    }
  });
}

let scatterChartInstance;
function renderScatterChart(scatterData) {
  if (scatterChartInstance) scatterChartInstance.destroy();

  // Format points to ensure they match {x, y}
  const points = (scatterData.points || []).map(p => ({ x: p.x, y: p.y }));

  scatterChartInstance = new Chart(scatterCanvas, {
    type: "scatter",
    data: {
      datasets: [{
        label: "Protein vs Carbs",
        data: points,
        backgroundColor: "rgba(16, 185, 129, 0.6)",
        borderColor: "rgb(16, 185, 129)",
        pointRadius: 5,
        pointHoverRadius: 7
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
            display: true,
            text: "Protein (g)"
          }
        },
        y: {
          title: {
            display: true,
            text: "Carbs (g)"
          }
        }
      }
    }
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
          "rgba(239, 68, 68, 0.7)",
          "rgba(16, 185, 129, 0.7)",
          "rgba(139, 92, 246, 0.7)"
        ]
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

function renderHeatmap(heatmapData) {
  if (!heatmapData || heatmapData.length === 0) {
    heatmapDiv.innerHTML = "<p class='text-sm text-gray-500 flex items-center justify-center h-full'>No heatmap data available</p>";
    return;
  }
  const labels = ["Calories", "Protein", "Fat"];
  let html = `<table class="w-full h-full text-xs text-center border-collapse">`;

  // Header row
  html += `<thead><tr><th class="p-1 border border-gray-300 bg-gray-50"></th>`;
  labels.forEach(label => {
    html += `<th class="p-1 border border-gray-300 bg-gray-50 font-semibold">${label}</th>`;
  });
  html += `</tr></thead><tbody>`;

  // Data rows
  for (let i = 0; i < heatmapData.length; i++) {
    html += `<tr><td class="p-1 border border-gray-300 bg-gray-50 font-semibold text-left">${labels[i] || `Var ${i + 1}`}</td>`;
    for (let j = 0; j < heatmapData[i].length; j++) {
      const val = heatmapData[i][j];
      const absVal = Math.abs(val);
      // Determine background color based on correlation strength (positive/negative)
      let bgColor = "rgba(239, 68, 68, 0)"; // Transparent for 0
      if (val > 0) {
        bgColor = `rgba(37, 99, 235, ${absVal})`; // Blue for positive correlation
      } else {
        bgColor = `rgba(239, 68, 68, ${absVal})`; // Red for negative correlation
      }
      const textColor = absVal > 0.5 ? "text-white" : "text-gray-800";
      html += `<td class="p-2 border border-gray-300 ${textColor}" style="background-color: ${bgColor}; font-weight: 500;">${val.toFixed(2)}</td>`;
    }
    html += `</tr>`;
  }
  html += `</tbody></table>`;
  heatmapDiv.innerHTML = html;
}

function renderMetadata(executionTime) {
  metadataEl.textContent = `Execution time: ${executionTime}`;
}

// Event Listeners for dynamic updates
btnInsights.addEventListener("click", () => {
  fetchInsights();
});

dietSelect.addEventListener("change", () => {
  fetchInsights();
});

// Use debounce or search keyup event for input search
let searchTimeout;
dietSearch.addEventListener("input", () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchInsights();
  }, 400); // 400ms debounce
});

// Setup fallback or other button handlers
document.getElementById("btnRecipes").addEventListener("click", () => {
  alert("Recipes functionality is connected and fetched via the dynamic filters dashboard!");
});

document.getElementById("btnClusters").addEventListener("click", () => {
  alert("Clusters visualization and insights are integrated into the scatter and heatmap diagrams!");
});

// initial load
document.addEventListener("DOMContentLoaded", () => {
  fetchInsights();
});
