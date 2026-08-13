/* =============================================================================
   AUTH ADDITIONS — Group 3 (Security & Authentication)
   Redirects to login.html if no token, validates session, injects user bar.
   ============================================================================= */

(function () {
  const API_BASE = "https://diet-insights-func-20260811-plan.azurewebsites.net/api";

  const token = localStorage.getItem("authToken");
  const email = localStorage.getItem("userEmail");

  if (!token) {
    window.location.href = "login.html";
    return;
  }

  fetch(`${API_BASE}/get_me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
    .then((res) => {
      if (!res.ok) {
        localStorage.removeItem("authToken");
        localStorage.removeItem("userEmail");
        window.location.href = "login.html";
      }
    })
    .catch(() => {
      // Network hiccup — don't force logout, proceed with cached session.
    });

  function renderUserBar() {
    const bar = document.createElement("div");
    bar.id = "user-session-bar";
    bar.style.cssText = `
      position: fixed;
      top: 16px;
      right: 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 8px 14px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 0.85rem;
      color: #f1f5f9;
      z-index: 1000;
    `;
    const emailSpan = document.createElement("span");
    emailSpan.textContent = email || "";
    const logoutBtn = document.createElement("button");
    logoutBtn.textContent = "Log out";
    logoutBtn.style.cssText = `
      background: #ef4444;
      color: white;
      border: none;
      border-radius: 6px;
      padding: 6px 10px;
      cursor: pointer;
      font-size: 0.8rem;
    `;
    logoutBtn.addEventListener("click", () => {
      localStorage.removeItem("authToken");
      localStorage.removeItem("userEmail");
      window.location.href = "login.html";
    });
    bar.appendChild(emailSpan);
    bar.appendChild(logoutBtn);
    document.body.appendChild(bar);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderUserBar);
  } else {
    renderUserBar();
  }

  window.authFetch = function (url, options = {}) {
    const headers = Object.assign({}, options.headers, {
      Authorization: `Bearer ${token}`,
    });
    return fetch(url, Object.assign({}, options, { headers }));
  };
})();

/* =============================================================================
   GROUP 1 — Dashboard logic (unchanged)
   ============================================================================= */

const FUNCTION_URL = "https://diet-insights-func-20260811-plan.azurewebsites.net/api/get_nutritional_insights";
const barCanvas = document.getElementById("barChart");
const scatterCanvas = document.getElementById("scatterPlot");
const pieCanvas = document.getElementById("pieChart");
const heatmapDiv = document.getElementById("heatmap");
const metadataEl = document.getElementById("metadata");

const dietSearch = document.getElementById("dietSearch");
const dietSelect = document.getElementById("dietSelect");
const btnInsights = document.getElementById("btnInsights");

async function fetchInsights() {
  try {
    metadataEl.textContent = "Loading insights...";
    const url = new URL(FUNCTION_URL);

    const selectedDiet = dietSelect.value;
    if (selectedDiet && selectedDiet !== "all") {
      url.searchParams.set("dietType", selectedDiet);
    }

    const searchVal = dietSearch.value.trim();
    if (searchVal) {
      url.searchParams.set("search", searchVal);
    }

    console.log("Fetching from URL:", url.toString());
    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();
    console.log("Data received:", data);

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
          "rgba(37, 99, 235, 0.7)",
          "rgba(245, 158, 11, 0.7)",
          "rgba(16, 185, 129, 0.7)"
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
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Amount (g)' }
        }
      }
    }
  });
}

let scatterChartInstance;
function renderScatterChart(scatterData) {
  if (scatterChartInstance) scatterChartInstance.destroy();
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
        x: { title: { display: true, text: "Protein (g)" } },
        y: { title: { display: true, text: "Carbs (g)" } }
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
  html += `<thead><tr><th class="p-1 border border-gray-300 bg-gray-50"></th>`;
  labels.forEach(label => {
    html += `<th class="p-1 border border-gray-300 bg-gray-50 font-semibold">${label}</th>`;
  });
  html += `</tr></thead><tbody>`;
  for (let i = 0; i < heatmapData.length; i++) {
    html += `<tr><td class="p-1 border border-gray-300 bg-gray-50 font-semibold text-left">${labels[i] || `Var ${i + 1}`}</td>`;
    for (let j = 0; j < heatmapData[i].length; j++) {
      const val = heatmapData[i][j];
      const absVal = Math.abs(val);
      let bgColor = val > 0
        ? `rgba(37, 99, 235, ${absVal})`
        : `rgba(239, 68, 68, ${absVal})`;
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

btnInsights.addEventListener("click", () => fetchInsights());

document.getElementById("btnClusters").addEventListener("click", () => {
  alert("Clusters visualization and insights are integrated into the scatter and heatmap diagrams!");
});

// Group 2 — filter/search/pagination
const RECIPES_URL = "https://diet-insights-func-20260811-plan.azurewebsites.net/api/recipes";
let currentPage = 1;
let searchTimeout;

async function fetchRecipes(page = 1) {
  const diet = dietSelect.value;
  const search = dietSearch.value.trim();
  const url = new URL(RECIPES_URL);
  if (diet && diet !== "all") url.searchParams.set("diet", diet);
  if (search) url.searchParams.set("search", search);
  url.searchParams.set("page", page);
  url.searchParams.set("page_size", 10);

  try {
    const res = await fetch(url);
    const data = await res.json();
    currentPage = data.page;

    const table = document.getElementById("recipesTable");
    if (!data.results || data.results.length === 0) {
      table.innerHTML = "<p class='text-sm text-gray-500'>No recipes found.</p>";
    } else {
      let html = `<table class="w-full text-sm border-collapse">
        <thead><tr class="bg-gray-200">
          <th class="p-2 text-left border">Recipe</th>
          <th class="p-2 text-left border">Diet</th>
          <th class="p-2 text-left border">Cuisine</th>
          <th class="p-2 text-left border">Protein(g)</th>
          <th class="p-2 text-left border">Carbs(g)</th>
          <th class="p-2 text-left border">Fat(g)</th>
        </tr></thead><tbody>`;
      data.results.forEach(r => {
        html += `<tr class="border-b hover:bg-gray-50">
          <td class="p-2 border">${r.Recipe_name || ""}</td>
          <td class="p-2 border">${r.Diet_type || ""}</td>
          <td class="p-2 border">${r.Cuisine_type || ""}</td>
          <td class="p-2 border">${r["Protein(g)"] || ""}</td>
          <td class="p-2 border">${r["Carbs(g)"] || ""}</td>
          <td class="p-2 border">${r["Fat(g)"] || ""}</td>
        </tr>`;
      });
      html += `</tbody></table>`;
      table.innerHTML = html;
    }

    document.getElementById("pageInfo").textContent = `Page ${data.page} of ${data.total_pages} (${data.total_items} results)`;
    document.getElementById("btnPrev").disabled = data.page <= 1;
    document.getElementById("btnNext").disabled = data.page >= data.total_pages;
  } catch (err) {
    console.error("Error fetching recipes:", err);
  }
}

document.getElementById("btnPrev").addEventListener("click", () => fetchRecipes(currentPage - 1));
document.getElementById("btnNext").addEventListener("click", () => fetchRecipes(currentPage + 1));
document.getElementById("btnRecipes").addEventListener("click", () => fetchRecipes(1));

dietSelect.addEventListener("change", () => { fetchRecipes(1); fetchInsights(); });
dietSearch.addEventListener("input", () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => { fetchRecipes(1); fetchInsights(); }, 400);
});

document.addEventListener("DOMContentLoaded", () => {
  console.log("Dashboard loaded. Fetching initial data...");
  fetchInsights();
  fetchRecipes(1);
});