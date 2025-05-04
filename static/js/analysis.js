// analysis.js
document.addEventListener("DOMContentLoaded", () => {
  // Static data
  const analysisData = {
    month: {
      income: {
        daily: [100, 200, 150, 300, 250, 400, 350, 500, 450, 600, 550, 700],
        categories: {
          Salary: 3000,
          Bonus: 1500,
          Investment: 2000,
        },
      },
      expense: {
        daily: [50, 100, 75, 150, 125, 200, 175, 250, 225, 300, 275, 350],
        categories: {
          Food: 1200,
          Rent: 1800,
          Entertainment: 800,
        },
      },
    },
  };

  // Chart instances
  let lineChart, pieChart;

  // Initialize charts
  function initCharts() {
    destroyCharts();
    const isMonthly =
      document.querySelector("[data-period].active").dataset.period === "month";
    const type = document.getElementById("analysisType").value;

    // Line chart
    const lineCtx = document.getElementById("lineChart").getContext("2d");
    lineChart = new Chart(lineCtx, {
      type: "line",
      data: getLineData(type, isMonthly),
      options: { responsive: true, maintainAspectRatio: false },
    });

    // Pie chart
    const pieCtx = document.getElementById("pieChart").getContext("2d");
    pieChart = new Chart(pieCtx, {
      type: "pie",
      data: getPieData(type, isMonthly),
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  // Get data for the line chart
  function getLineData(type, isMonthly) {
    const labels = isMonthly
      ? Array.from({ length: 31 }, (_, i) => i + 1)
      : [
          "Jan",
          "Feb",
          "Mar",
          "Apr",
          "May",
          "Jun",
          "Jul",
          "Aug",
          "Sep",
          "Oct",
          "Nov",
          "Dec",
        ];

    const dataset = {
      label: type.toUpperCase(),
      data: isMonthly
        ? analysisData.month[type].daily
        : analysisData.year[type].monthly,
      borderColor: type === "income" ? "#28a745" : "#dc3545",
      tension: 0.4,
    };

    return { labels, datasets: [dataset] };
  }

  // Get data for the pie chart
  function getPieData(type, isMonthly) {
    const categories = isMonthly
      ? analysisData.month[type].categories
      : analysisData.year[type].categories;

    return {
      labels: Object.keys(categories),
      datasets: [
        {
          data: Object.values(categories),
          backgroundColor: [
            "#FF6384",
            "#36A2EB",
            "#FFCE56",
            "#4BC0C0",
            "#9966FF",
          ],
        },
      ],
    };
  }

  // Render the ranking list
  function renderRanking() {
    const container = document.getElementById("rankingList");
    const isMonthly =
      document.querySelector("[data-period].active").dataset.period === "month";
    const type = document.getElementById("analysisType").value;
    const categories = isMonthly
      ? analysisData.month[type].categories
      : analysisData.year[type].categories;

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
          <div class="text-muted" style="width: 60px">${(
            (value / maxValue) *
            100
          ).toFixed()}%</div>
        </div>
      `
      )
      .join("");
  }

  // Destroy old charts
  function destroyCharts() {
    if (lineChart) lineChart.destroy();
    if (pieChart) pieChart.destroy();
  }

  // Event listeners
  document.querySelectorAll("[data-period]").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      document
        .querySelectorAll("[data-period]")
        .forEach((b) => b.classList.remove("active"));
      this.classList.add("active");
      initCharts();
      renderRanking();
    });
  });

  document.getElementById("analysisType").addEventListener("change", () => {
    initCharts();
    renderRanking();
  });

  // Initialize
  initCharts();
  renderRanking();
});
