// CKYC Dashboard - client side chart rendering + filters
document.addEventListener("DOMContentLoaded", function () {

  // ---- Partner bar chart (Chart.js) ----
  var chartData = window.CKYC_CHART_DATA;
  var canvas = document.getElementById("partnerChart");
  if (canvas && chartData && chartData.labels && chartData.labels.length) {
    var palette = ["#4e8cc7", "#6fb98f", "#e0a83e", "#c96b6b", "#8f6fc9", "#4ecdc4", "#e07a5f"];
    var colors = chartData.labels.map(function (_, i) { return palette[i % palette.length]; });

    new Chart(canvas.getContext("2d"), {
      type: "bar",
      data: {
        labels: chartData.labels,
        datasets: [{
          label: "Cases",
          data: chartData.values,
          backgroundColor: colors,
          borderRadius: 4,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: "#fff" }, grid: { color: "rgba(255,255,255,0.1)" } },
          y: { ticks: { color: "#fff" }, grid: { color: "rgba(255,255,255,0.1)" }, beginAtZero: true },
        },
      },
    });
  }

  // ---- Client-side filters: Product / Status drive /api/drilldown highlighting ----
  var productSel = document.getElementById("filter-product");
  var statusSel = document.getElementById("filter-status");

  function applyFilters() {
    if (!productSel || !statusSel) return;
    var product = productSel.value;
    var status = statusSel.value;

    var params = new URLSearchParams({ product: product, bucket: status, partner: "All" });
    fetch("/api/drilldown?" + params.toString())
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var countEl = document.querySelector(".side-panel p strong");
        if (countEl) {
          countEl.textContent = data.count;
        }
      })
      .catch(function () { /* ignore network errors client-side */ });
  }

  if (productSel) productSel.addEventListener("change", applyFilters);
  if (statusSel) statusSel.addEventListener("change", applyFilters);
});
