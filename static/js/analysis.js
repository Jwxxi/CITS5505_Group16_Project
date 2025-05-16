// static/js/analysis.js

document.addEventListener("DOMContentLoaded", () => {
  const typeSelect = document.getElementById("analysisType");
  const yearSelect = document.getElementById("analysisYear");
  const monthSelect = document.getElementById("analysisMonth");
  const applyBtn = document.getElementById("applyAnalysisFilter");
  const tableBody = document.getElementById("analysisTableBody");
  let allData = [];

  const categoryChartCtx = document.getElementById("categoryChart").getContext("2d");
  const monthlyChartCtx = document.getElementById("monthlyChart").getContext("2d");
  let categoryChart;
  let monthlyChart;

  async function fetchData() {
    try {
      const res = await fetch("/api/transactions");
      const data = await res.json();
      allData = data;
      populateYears(data);
      renderAnalysis();
    } catch (err) {
      console.error("Failed to load data", err);
    }
  }

  function populateYears(data) {
    const years = new Set(data.map(tx => new Date(tx.date).getFullYear()));
    yearSelect.innerHTML = '<option value="">Select Year</option>';
    [...years].sort().forEach(year => {
      yearSelect.innerHTML += `<option value="${year}">${year}</option>`;
    });
  }

  function renderAnalysis() {
    const selectedType = typeSelect.value;
    const selectedYear = yearSelect.value;
    const selectedMonth = monthSelect.value;

    let filtered = allData.filter(tx => tx.type === selectedType);

    if (selectedYear) {
      filtered = filtered.filter(tx => new Date(tx.date).getFullYear().toString() === selectedYear);
    }

    if (selectedMonth) {
      filtered = filtered.filter(tx => (new Date(tx.date).getMonth() + 1).toString() === selectedMonth);
    }

    updateTable(filtered);
    drawCategoryChart(filtered);
    drawMonthlyChart(filtered);
  }

  function updateTable(data) {
    tableBody.innerHTML = "";
    data.forEach(tx => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${new Date(tx.date).toLocaleDateString()}</td>
        <td>${tx.category}</td>
        <td>${tx.description || "-"}</td>
        <td class="${tx.type === "income" ? "text-success" : "text-danger"}">$${tx.amount.toFixed(2)}</td>
      `;
      tableBody.appendChild(row);
    });
  }

  function drawCategoryChart(data) {
    const grouped = {};
    data.forEach(tx => {
      grouped[tx.category] = (grouped[tx.category] || 0) + tx.amount;
    });

    const labels = Object.keys(grouped);
    const values = Object.values(grouped);

    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(categoryChartCtx, {
      type: "pie",
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: labels.map(() => `hsl(${Math.random() * 360}, 70%, 60%)`),
        }],
      },
    });
  }

  function drawMonthlyChart(data) {
    const monthlyTotals = Array(12).fill(0);
    data.forEach(tx => {
      const monthIndex = new Date(tx.date).getMonth();
      monthlyTotals[monthIndex] += tx.amount;
    });

    const monthLabels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

    if (monthlyChart) monthlyChart.destroy();
    monthlyChart = new Chart(monthlyChartCtx, {
      type: "line",
      data: {
        labels: monthLabels,
        datasets: [{
          label: `${typeSelect.value.charAt(0).toUpperCase() + typeSelect.value.slice(1)} Trend`,
          data: monthlyTotals,
          fill: false,
          tension: 0.3,
          borderColor: "#0dcaf0",
          pointBackgroundColor: "#fff"
        }],
      },
    });
  }

  applyBtn.addEventListener("click", renderAnalysis);

  fetchData();
});
