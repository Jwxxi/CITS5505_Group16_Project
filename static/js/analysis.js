// analysis.js
document.addEventListener("DOMContentLoaded", () => {
  // Fetch analysis data from the backend
  async function fetchAnalysis(type) {
    try {
      const response = await fetch(`/api/analysis?type=${type}`);
      const data = await response.json();
      renderCharts(data.categories);
      renderRanking(data.categories);
    } catch (error) {
      console.error("Error fetching analysis data:", error);
    }
  }

  // Render charts
  function renderCharts(categories) {
    const labels = Object.keys(categories);
    const data = Object.values(categories);

    // Pie chart
    const pieCtx = document.getElementById("pieChart").getContext("2d");
    new Chart(pieCtx, {
      type: "pie",
      data: {
        labels,
        datasets: [
          {
            data,
            backgroundColor: [
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#4BC0C0",
              "#9966FF",
            ],
          },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  // Render ranking
  function renderRanking(categories) {
    const container = document.getElementById("rankingList");
    const sorted = Object.entries(categories).sort((a, b) => b[1] - a[1]);
    const maxValue = sorted[0][1];

    container.innerHTML = sorted
      .map(
        ([category, value]) => `
        <div class="ranking-item">
          <div class="ranking-label">${category}</div>
          <div class="ranking-value">$${value.toFixed(2)}</div>
          <div class="progress-bar" style="width: ${(
            (value / maxValue) *
            100
          ).toFixed()}%"></div>
        </div>
      `
      )
      .join("");
  }

  // Event listeners
  document.getElementById("analysisType").addEventListener("change", (e) => {
    fetchAnalysis(e.target.value);
  });

  // Initial fetch
  fetchAnalysis("expense");
});
